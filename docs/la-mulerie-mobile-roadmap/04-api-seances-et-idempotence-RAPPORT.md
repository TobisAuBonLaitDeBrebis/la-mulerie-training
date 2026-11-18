# Lot 04 — API des séances et création idempotente — **COMPTE RENDU**

**Date :** à compléter  
**Version :** 1.0  
**Auteur :** Agent de code  
**Statut :** ✅ **TERMINÉ**

---

## 📋 Sommaire

1. [Résumé](#1-résumé)
2. [Analyse préalable](#2-analyse-préalable)
3. [Modèle : champ `client_uuid` et migration](#3-modèle--champ-client_uuid-et-migration)
4. [Endpoints implémentés](#4-endpoints-implémentés)
5. [Idempotence : conception](#5-idempotence--conception)
6. [Tests](#6-tests)
7. [Points d'attention et limites](#7-points-dattention-et-limites)

---

## 1. Résumé

Le **Lot 04** expose les séances d'entraînement au mobile et permet leur création avec une garantie d'idempotence par UUID client.

- ✅ `GET /api/v1/sessions/` : liste paginée filtrée sur le cavalier authentifié
- ✅ `GET /api/v1/sessions/{id}/` : détail d'une séance autorisée (404 sinon)
- ✅ `POST /api/v1/sessions/` : création validée serveur, idempotente via `client_uuid`
- ✅ Contrainte unique en base `(cavalier, client_uuid)` + gestion des collisions concurrentes
- ✅ 21 nouveaux tests API, suite complète à 85/85
- ✅ Aucune régression web (47 tests web verts)
- ✅ `python manage.py check` sans erreur

---

## 2. Analyse préalable

### Relation acteur / séance (confirmée dans le code web)

- `TrainingSession.cavalier` est **toujours** l'utilisateur authentifié : posé par le serveur dans `training_add` (`training.cavalier = request.user`) et `training_edit`, et le formulaire web (`TrainingSessionForm`) n'inclut ni `cheval` côté route, ni `cavalier`.
- Les listes/détails web filtrent sur `cavalier=request.user` (`home_training`, dashboard, `training_detail`, `training_edit`, `training_delete`).
- Le cheval référencé doit appartenir à l'utilisateur (`Horse.objects.filter(proprietaire=request.user)` dans `training_add`).

**Règle API retenue (identique au web) :** le cavalier d'une séance API est `request.user` ; la séance n'est visible que par son cavalier ; le cheval doit appartenir à l'utilisateur.

### Champs et validations

Repris du modèle et des vues web existants, sans changement de sémantique :

- `date` : `DateField` (date locale métier, pas de conversion UTC).
- `type_seance` : `CharField(100)` requis.
- `duree` : minutes entières, `>= 1` (validateur + contrainte DB).
- `cout` : euros, `Decimal(7,2)`, optionnel, `>= 0` (validateur + contrainte DB).
- `notes` : texte optionnel.
- `cavalier` : dérivé serveur, jamais lu du payload.

---

## 3. Modèle : champ `client_uuid` et migration

### Choix retenu : champ sur le modèle + contrainte scopée

Le couple `(cavalier, client_uuid)` identifie la création de façon sûre :

- **Scopé par l'acteur** : deux utilisateurs peuvent légitimement générer le même UUID → contrainte sur les deux colonnes, pas globale.
- **Nullable et sans risque** : `client_uuid = models.UUIDField(null=True, blank=True)` sans défaut. Les séances web historiques ont `client_uuid = NULL` ; SQL traite les NULLs comme distinctes dans une contrainte unique (`UniqueConstraint(fields=['cavalier', 'client_uuid'])`), donc plusieurs séances sans UUID coexistent. Un défaut automatique a été écarté : il masquerait l'oubli de l'UUID côté mobile et casserait l'idempotence (nouvel UUID à chaque retry).
- La clé d'idempotence et la séance sont **la même ligne** : l'enregistrement de `K` et la création sont atomiques par construction, et protégés par la contrainte en base.

### Migration `0007_trainingsession_client_uuid_and_more`

- `AddField client_uuid` (NULL pour toutes les lignes existantes, aucune donnée inventée).
- Complète aussi les contraintes `cout_non_negatif`, `duree_positive` (déclarées dans le `Meta` du lot 01 mais qui n'apparaissaient dans l'état d'aucune migration antérieure — la 0006 ne les avait pas enregistrées) et pose `uniq_cavalier_client_uuid`.
- Aucune transformation de données historiques.

---

## 4. Endpoints implémentés

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|------------------|
| `/api/v1/sessions/` | GET | Liste paginée des séances du cavalier (20/page) | JWT requis |
| `/api/v1/sessions/{id}/` | GET | Détail d'une séance autorisée (404 si d'autrui ou inexistante) | JWT requis |
| `/api/v1/sessions/` | POST | Création idempotente (201 / 200 replay / 409 conflit / 400 validation) | JWT requis |

### Payload de création

```json
{
    "client_uuid": "e5a5b3f2-...-...",
    "cheval": 1,
    "date": "2025-11-10",
    "type_seance": "dressage",
    "duree": 45,
    "cout": "50.00",
    "notes": "..."
}
```

- `client_uuid` : **requis**, UUID généré par le mobile avant l'envoi et conservé lors des retries.
- `cheval` : id d'un équidé de l'utilisateur ; le queryset du champ est restreint à `proprietaire=request.user`, donc un équidé d'autrui ou inexistant produit la même erreur 400 (pas de fuite d'existence).
- `cavalier` ignoré s'il est fourni.
- Unités documentées dans le serializer : `duree` en minutes, `cout` en euros (schéma OpenAPI complet : lot 05).

---

## 5. Idempotence : conception

Comportement implémenté dans `TrainingSessionListView.create` :

1. **Rejet en amont** : UUID absent ou invalide → 400, rien n'est créé (une création sans clé n'est pas idempotente donc refusée).
2. **Chemin rapide** : une séance existe déjà pour `(cavalier, client_uuid)` → contenu identique → **200** avec la séance existante (pas de doublon).
3. **Conflit** : même clé, contenu différent → **409** avec `detail` et `session_id`, la séance originale n'est jamais écrasée.
4. **Collision concurrente** : création dans `transaction.atomic()` ; si un concurrent commite la même clé entre le chemin rapide et l'INSERT, l'`IntegrityError` est capté, la séance gagnante est relue et renvoyée (200) — ou 409 si le contenu diffère. La contrainte unique en base est le garant final du non-doublon.
5. **Validation** en 400 structurée via le handler DRF, sans séance partielle (le save est unique et atomique).

La comparaison de contenu (`payload_matches` dans `api/serializers.py`) porte sur `cheval`, `date`, `type_seance`, `duree`, `cout`, `notes`.

### Choix documentés

- La détection de conflit compare le **contenu du payload à l'état courant** de la séance. Conséquence : si une séance est modifiée après création puis que le mobile rejoue la création originale avec `K`, la réponse est 409. Une évolution possible (lot future) : enregistrer un hash du payload par clé d'idempotence pour ne jamais 409 sur un rejeu.
- Pas de filtres additionnels (`cheval`, dates) tant qu'aucun besoin mobile concret n'est exprimé.

---

## 6. Tests

### Tests ajoutés (`api/test_api.py`, 21 tests)

**Lecture (`TrainingSessionApiTestCase`)**

| Test | Vérification |
|------|--------------|
| `test_list_requires_authentication` / `test_detail_requires_authentication` | 401 pour anonyme |
| `test_list_returns_only_own_sessions` | Isolation par cavalier |
| `test_detail_of_other_user_session_returns_404` / `test_detail_of_own_session_returns_200` | Détail filtré |
| `test_create_returns_201_with_data` | Création nominale, `client_uuid` et valeurs persistées |
| `test_create_ignores_cavalier_from_payload` | Le payload ne peut pas désigner l'acteur |
| `test_create_with_inaccessible_horse_refused` / `test_create_with_nonexistent_horse_refused` | Équidé invalidé en 400 |
| `test_create_missing_fields_returns_400_without_partial_session` | 400, aucune séance partielle |
| `test_create_with_invalid_client_uuid_refused` / `test_create_missing_client_uuid_refused` | UUID requis et valide |
| `test_create_requires_authentication` | POST anonyme refusé |

**Idempotence**

| Test | Vérification |
|------|--------------|
| `test_replay_same_uuid_same_payload_returns_existing` | 200, même id, 1 seule ligne |
| `test_replay_same_uuid_different_payload_returns_409` | 409, séance originale intacte |
| `test_same_uuid_from_another_user_is_isolated` | Autre cavalier, même UUID : sa propre séance, aucune fuite |
| `test_web_sessions_without_uuid_remain_allowed` | Séances web à `NULL` toujours possibles (nulls distincts) |
| `test_unique_constraint_blocks_duplicate_key` | La contrainte DB bloque le doublon |

**Collisions concurrentes (déterministes, `TrainingSessionCollisionTestCase`)**

| Test | Vérification |
|------|--------------|
| `test_collision_with_same_payload_returns_existing_session` | Perdant → 200, 1 seule ligne pour la clé |
| `test_collision_with_different_payload_returns_409` | Perdant → 409, gagnant intact |
| `TrainingSessionConcurrencyTestCase::test_two_creations_same_key_use_single_row` | CREATE en double → `IntegrityError`, une seule ligne |

Les tests de collision simulent deux créateurs simultanés de façon **déterministe** : le gagnant commite sa séance puis l'INSERT du perdant échoue sur la contrainte. Un test threadé réel a été écarté (voir limites).

### Commandes exécutées et résultats

```
.venv/Scripts/python.exe -m pytest api/test_api.py   → 38 passed
.venv/Scripts/python.exe -m pytest                    → 85 passed (47 web + 38 API)
.venv/Scripts/python.exe manage.py check              → aucun problème
.venv/Scripts/python.exe manage.py makemigrations training → 0007 générée et relue
```

Parcours web et formulaires : inchangés (aucun fichier `training/views.py`, `training/forms.py`, template modifié ; seuleajout du champ nullable + contrainte dans `training/models.py`).

---

## 7. Points d'attention et limites

1. **Test threadé réel écarté** : SQLite en mémoire partagée entre deux connexions (mode utilisé par Django pour les tests) lève immédiatement `database table is locked` entre deux écrivains — un test threadé serait instable. La garantie de non-doublon est couverte de façon déterministe par les tests de collision et par la contrainte en base, valable sur le SGBD de production.
2. **409 basé sur l'état courant** : un rejeu après modification de la séance répondra 409 même si le contenu rejoué est celui de la création initiale. Acceptable peut-être pour un rejeu post-connexion réseau (le payload mobile correspond à ce qu'il vient d'envoyer) ; à arbitrer si le produit introduit l'édition.
3. **`client_uuid` unique par cavalier** : la même valeur peut exister chez deux cavaliers (comportement voulu, pas de fuite — testé).
4. **Ordre de la liste** : tri sur `id` (stabilité de pagination), pas sur `date` comme la vue web `home_training`. À ajuster selon les écrans mobiles.
5. **Validation duree PositiveIntegerField** : `0` passe la validation de type mais `MinValueValidator(1)` + contrainte DB → 400.
6. Hors périmètre conservé : édition/suppression offline, sync locale, upload de fichiers.

---

**Prochaine étape :** Lot 05 — Dashboard API et OpenAPI.
