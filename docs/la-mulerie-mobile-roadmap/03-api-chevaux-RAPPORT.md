# Lot 03 — API des équidés — **COMPTE RENDU**

**Date :** à compléter  
**Version :** 1.0  
**Auteur :** Agent de code  
**Statut :** ✅ **TERMINÉ**

---

## 📋 Sommaire

1. [Résumé](#1-résumé)
2. [Analyse préalable](#2-analyse-préalable)
3. [Fichiers créés/modifiés](#3-fichiers-créésmodifiés)
4. [Endpoints implémentés](#4-endpoints-implémentés)
5. [Décisions de conception](#5-décisions-de-conception)
6. [Tests](#6-tests)
7. [Points d'attention et limites](#7-points-dattention-et-limites)

---

## 1. Résumé

Le **Lot 03** expose la liste et le détail des équidés à l'application mobile, en lecture seule, avec les droits d'accès validés au lot 01 (un utilisateur ne voit que les équidés dont il est propriétaire).

- ✅ `GET /api/v1/horses/` : liste paginée (20 par page), filtrée sur le propriétaire authentifié
- ✅ `GET /api/v1/horses/{id}/` : détail d'un équidé accessible, 404 sinon (sans révéler l'existence)
- ✅ Serializer de lecture dédié : pas d'exposition du propriétaire ni des champs internes
- ✅ 10 nouveaux tests API, suite complète à 64/64
- ✅ Aucune régression web (47 tests existants inchangés et verts)
- ✅ `python manage.py check` : aucun problème

L'écriture (création/modification/suppression) reste hors périmètre MVP, conformément au cahier des charges du lot.

---

## 2. Analyse préalable

### Modèle `Horse` (`training/models.py`)

| Champ | Type | Notes |
|-------|------|-------|
| `nom` | `CharField(100)` | |
| `race` | `CharField(100)` | |
| `birth_date` | `DateField` | |
| `proprietaire` | FK `User` (non nullable, règle lot 01) | `related_name='chevaux'` |
| `age` | propriété calculée (années) | non stockée |

Le modèle n'a **pas** de champ `updated_at` : il n'est donc pas exposé (sa sémantique n'existerait pas).

### Règle d'accès (issue du lot 01)

Un utilisateur n'accède qu'à **ses propres** équidés (`proprietaire=request.user`). Aucun mécanisme de partage (cavaliers autorisés) n'existe encore dans le modèle ; il n'a donc pas été simulé.

### Validations web

`HorseForm` (web) gère `nom`, `race`, `birth_date`, `proprietaire`. Sans importance pour une API de lecture seule, mais confirme le périmètre des champs utiles au mobile.

---

## 3. Fichiers créés/modifiés

| Fichier | Type | Description |
|---------|------|-------------|
| `api/serializers.py` | ⚡ Modifié | Ajout de `HorseSerializer` (lecture seule : `id`, `nom`, `race`, `birth_date`, `age`) |
| `api/views.py` | ⚡ Modifié | Ajout de `HorseListView` (ListAPIView) et `HorseDetailView` (RetrieveAPIView) |
| `api/urls.py` | ⚡ Modifié | Routes `horses/` et `horses/<int:pk>/` (names `horse-list`, `horse-detail`) |
| `api/tests.py` → `api/test_api.py` | ⚡ Renommé + Modifié | 10 tests ajoutés pour les chevaux (voir section 6) |
| `docs/la-mulerie-mobile-roadmap/03-api-chevaux-RAPPORT.md` | ✨ Nouveau | Ce rapport |

**Renommage justifié :** `pytest.ini` impose `python_files = test_*.py`. Le fichier `api/tests.py` créé au lot 02 n'était donc **jamais collecté** par la suite complète `pytest` (seulement 47 tests étaient lancés, les 7 tests API ignorés silencieusement). Le renommage en `api/test_api.py` restaure la collecte : la suite est passée de 47 à 64 tests.

---

## 4. Endpoints implémentés

| Endpoint | Méthode | Description | Authentification |
|----------|---------|-------------|------------------|
| `/api/v1/horses/` | GET | Liste des équidés du propriétaire authentifié, paginée (20/page) | JWT requis |
| `/api/v1/horses/{id}/` | GET | Détail d'un équidé accessible (404 si non autorisé ou inexistant) | JWT requis |

### Format de `/api/v1/horses/`

```json
{
    "count": 25,
    "next": "http://…/api/v1/horses/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "nom": "Morange",
            "race": "Mulet",
            "birth_date": "2020-11-13",
            "age": 5
        }
    ]
}
```

- Pagination : `PageNumberPagination` DRF héritée de la config du lot 02, `PAGE_SIZE = 20`. Le format (`count` / `next` / `previous` / `results`) est stable.
- Le détail renvoie directement l'objet (sans enveloppe de pagination).
- Aucun filtre supplémentaire n'est exposé : aucun besoin mobile concret à ce stade.

---

## 5. Décisions de conception

### A. Sérialisation

`HorseSerializer` est un `ModelSerializer` en lecture seule :

- `id`, `nom`, `race`, `birth_date` : champs du modèle ;
- `age` : propriété calculée exposée via `IntegerField(read_only=True)` ;
- **`proprietaire` non exposé** : la règle d'accès du lot 01 limite la lecture au propriétaire lui-même, l'information est redondante et sa suppression limite l'exposition de données personnelles ;
- **pas d'`updated_at`** : le champ n'existe pas sur le modèle.

### B. Permissions

- Les deux vues héritent de `IsAuthenticated` (config DRF du lot 02) ; un utilisateur anonyme reçoit 401.
- Le filtrage est appliqué **au niveau queryset** (`Horse.objects.filter(proprietaire=self.request.user)`) et non en permission objet a posteriori. C'est la même approche que les vues web du lot 01, une seule source de vérité.
- `RetrieveAPIView.get_object()` consomme le queryset filtré : un équidé non autorisé ou inexistant renvoie **404** identique, sans révéler l'existence de la ressource.
- Aucune donnée fournie par le client n'est acceptée (pas de mutation) ; toute future écriture devra dériver le propriétaire côté serveur (`request.user`), jamais du payload.

### C. Réutilisation du métier

La lecture est une simple queryset filtrée : pas de selector ni d'abstraction supplémentaire, conformément au lot et aux principes du projet (pas de couche inutile).

---

## 6. Tests

### Tests ajoutés (`api/test_api.py`, classe `HorseApiTestCase`, 10 tests)

| Test | Vérification |
|------|--------------|
| `test_list_requires_authentication` | La liste refuse un anonyme (401) |
| `test_detail_requires_authentication` | Le détail refuse un anonyme (401) |
| `test_list_returns_empty_list_when_no_horses` | Liste vide : `count=0`, `results=[]` |
| `test_list_returns_only_own_horses` | Les chevaux d'un autre utilisateur n'apparaissent pas |
| `test_list_returns_multiple_horses` | Tous les chevaux du propriétaire sont listés |
| `test_list_pagination` | 20 résultats page 1, `next` présent, 5 résultats page 2 |
| `test_list_exposed_fields_exact` | Champs exposés = exactement `{id, nom, race, birth_date, age}` |
| `test_detail_returns_horse` | Le détail d'un cheval autorisé renvoie 200 avec les bonnes valeurs |
| `test_detail_of_other_user_horse_returns_404` | Détail d'un cheval d'autrui → 404 (pas 403) |
| `test_detail_of_nonexistent_horse_returns_404` | Identifiant inexistant → 404 |

Les tests réutilisent les factories existantes (`UserFactory`, `HorseFactory` de `training/tests/factories.py`).

### Commandes exécutées et résultats

```
.venv/Scripts/python.exe -m pytest api/test_api.py   → 17 passed (7 JWT/me + 10 chevaux)
.venv/Scripts/python.exe -m pytest                    → 64 passed (47 web + 17 API)
.venv/Scripts/python.exe manage.py check              → aucun problème
```

### Régression web

Les 47 tests web du lot 01 et les vues/templates ne sont pas modifiés : aucune régression. Le site web continue d'utiliser ses sessions et ses formulaires ; l'API reste une lecture dédiée au mobile.

---

## 7. Points d'attention et limites

### Hypothèses prises

1. `age` est exposé au mobile bien qu'il ne soit pas demandé explicitement dans le lot : c'est une propriété calculée déjà utilisée, sans importance pour le calcul offline. À retirer si l'écran mobile ne l'utilise pas.
2. Aucun mécanisme de cavaliers autorisés/partage n'existant, la règle « propriétaire uniquement » est l'application littérale du lot 01. Si un partage est introduit plus tard, la queryset des vues est le seul point à étendre.
3. Le tri de la liste est fait sur `id` pour un ordre stable, la pagination ne pouvant pas tolérer un ordre indéterminé.

### Limites

1. **Collecte pytest** : le renommage `api/tests.py` → `api/test_api.py` doit être signalé, d'éventuelles documentations ou commandes citant `api/tests.py` sont à mettre à jour. Alternative possible (non retenue pour rester minimal) : convertir `api/tests.py` en package `api/tests/`.
2. **Throttling en test** : le throttling global (1000/h par utilisateur) est actif ; les tests restent très en dessous, mais une suite plus volumineuse devra en tenir compte.
3. **Avertissements Django 6** : `CheckConstraint(check=…)` est déprécié au profit de `condition=…` (déjà présent avant ce lot, hors périmètre).
4. **`birth_date` sérialisé** en chaîne ISO `YYYY-MM-DD` : le mobile doit parser la date, pas s'attendre à un objet.
5. Hors périmètre (non implémenté, conformément au lot) : création/modification/suppression, sync SQLite, écriture offline.

### Prochaines étapes

- Lot 04 : endpoints séances (`TrainingSession`) avec idempotence.
- Envisager une page de documentation des endpoints (lot 05 OpenAPI).

---
