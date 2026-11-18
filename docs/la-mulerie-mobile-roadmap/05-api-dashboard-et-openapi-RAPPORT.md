# Lot 05 — Dashboard API et contrat OpenAPI — **COMPTE RENDU**

**Date :** à compléter  
**Version :** 1.0  
**Auteur :** Agent de code  
**Statut :** ✅ **TERMINÉ**

---

## 1. Résumé

Le **Lot 05** extrait les calculs du tableau de bord dans un service partagé entre le web et le mobile, expose `GET /api/v1/dashboard/`, et documente l'ensemble de l'API v1 avec un schéma OpenAPI (drf-spectacular) qui se génère sans avertissement.

- ✅ `training/services.py` : composant commun `build_dashboard_data` appelé par la vue web (rendu et résultats inchangés, 12/12 tests web verts)
- ✅ `GET /api/v1/dashboard/` : JSON typé et stable, filtres inclusifs `start_date`/`end_date`
- ✅ 15 tests unitaires de calculs + 8 tests endpoint + 1 test de schéma
- ✅ Suite complète **109/109**, `manage.py check` sans erreur
- ✅ `manage.py spectacular --fail-on-warn` : 0 erreur, 0 warning
- ✅ SwaggerUI en développement, désactivée en production

## 2. Analyse préalable — indicateurs réellement affichés

Relevés dans la vue `dashboard` d'origine (`training/views.py`) puis extraits à l'identique :

| Indicateur | Définition / règles observées |
|---|---|
| `total_sessions` | Nombre de séances du **cavalier** authentifié, filtré par période |
| `total_horses` | Nombre d'équidés dont l'utilisateur est `proprietaire` (**non filtré** par la période) |
| `total_duration` | Somme de `duree`, en **minutes** |
| `total_cost` | Somme de `cout`, en **euros** (`Decimal`) |
| `sessions_by_type` | Comptage + durée cumulée par `type_seance`, tri par nombre décroissant |
| `sessions_by_horse` | Comptage + durée cumulée par cheval (clé web historique `cheval__nom`), tri par durée décroissante |
| `month_names` / `month_counts` | Sans filtre : 12 mois de **l'année en cours** (séances filtrées sur cette année). Avec filtre : plage min→max des mois **présents dans les données** (1→12 si aucune donnée) |
| `avg_duration` / `avg_cost` / `sessions_per_horse` | Moyennes arrondies à 1 (durée, séances/cheval) et 2 (coût) décimales ; 0 si pas de données |
| `recent_sessions` | 5 dernières séances triées par date décroissante |
| `sessions_dates` | Calendrier : `{id, date ISO, activity}` pour chaque séance (filtrée) |

Particularités conservées telles quelles (pas de changement de sémantique silencieux) :
- Les mois ignorés comptent sur **plusieurs années confondues** si la période couvre un chevauchement (comportement web historique) — documenté, à arbitrer au lot mobile si nécessaire.
- Dates et périodes : dates métier locales `YYYY-MM-DD`, **aucune conversion UTC**.
- Bornes `start_date` / `end_date` inclusives.
- Séances sans `cout` exclues des sommes de coût, comptées dans les totaux.

## 3. Partie A — Calculs métier partagés

- **`training/services.py`** : `build_dashboard_data(user, start_date=None, end_date=None)` retourne un dictionnaire plat reprenant exactement le contexte du template `dashboard.html` (clé `cheval__nom` conservée pour ne pas toucher le rendu web). La répartition mensuelle est isolée dans `_monthly_distribution`.
- **Vue web refactorée** : `dashboard` lit les deux paramètres GET, appelle le service, sérialise `sessions_dates` en JSON pour le calendrier et passe `start_date`/`end_date` au template. **Aucun rendu ni résultat modifié** : les 12 tests `test_dashboard.py` passent sans modification.
- Les deux interfaces consomment désormais une seule source de vérité : un indicateur évolue dans le service, jamais dans `training/views.py` ni côté React Native.

## 4. Partie B — Endpoint `/api/v1/dashboard/`

- `GET` (JWT requis), queryset interne filtrée sur `cavalier=request.user`.
- Filtres : `?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD` (validés en 400 si non conformes) ; la réponse renvoie la `period` effectivement appliquée (null = toutes les données).
- Payload de réponse (aucun objet Django brut) : `total_sessions`, `total_horses`, `total_duration` (minutes), `total_cost` (euros, nombre JSON), `avg_duration`, `avg_cost`, `sessions_per_horse`, `sessions_by_type[]`, `sessions_by_horse[]` (`cheval` = nom), `month_names[]`, `month_counts[]`, `recent_sessions[]` (`id`, `date`, `type_seance`, `cheval`, `duree`), `sessions_dates[]` (`id`, `date`, `activity`), `period`.
- Volume maîtrisé : tout est agrégé côté SQL ; seuls `recent_sessions` (5) et `sessions_dates` (calendrier de l'utilisateur filtré) ramènent des lignes — pas de pagination nécessaire après mesure du périmètre.

## 5. Partie C — OpenAPI (drf-spectacular 0.30.0)

Installé et enregistré (`requirements.txt`, `INSTALLED_APPS` des settings dev/prod/dev_test ; `DEFAULT_SCHEMA_CLASS` dans `settings/drf.py`).

| Route | Description |
|---|---|
| `/api/schema/` | Schéma OpenAPI 3 machine-readable (YAML/JSON), aucune donnée utilisateur |
| `/api/docs/` | SwaggerUI, **activée seulement si `API_SERVE_DOCS=True`** (dev : oui, prod : non) |

Contenu documenté :
- Authentification JWT (HTTP Bearer via SimpleJWT), pagination DRF.
- Schémas des réponses 200/201 de chaque endpoint (`/api/v1/me/`, horses, sessions, dashboard) avec **unités et formats de date** (aide `duree` en minutes, `cout` en euros, `YYYY-MM-DD` dans la description globale).
- Erreurs : schéma commun `ApiError` (`{error, code, message}` — enveloppe du handler `api/exceptions.py`) annoté 400/401/404.
- **Comportement 409 du POST des séances** : réponses 200/201/409 distinguées + description détaillée de la sémantique d'`client_uuid` (rejeu, conflit, contrainte `(cavalier, client_uuid)`).
- `manage.py spectacular --fail-on-warn` passe sans avertissement (2 warnings initiaux corrigés en annotant les paramètres du dashboard avec `OpenApiParameter`).
- Génération de types TypeScript : hors périmètre (facultatif au lot).

## 6. Tests

### Ajoutés

- **`training/tests/test_services.py` (15)** : totaux/moyennes sur jeux contrôlés, cheval sans séance, isolation cavalier vs propriétaire, répartitions (`type`/`horse`) exactes, filtres inclusifs aux bornes, dates string = dates objets, évolution mensuelle (année en cours / avec filtre / sans données), `recent_sessions` limité à 5, forme `sessions_dates`.
- **`api/test_api.py — DashboardApiTestCase (8)`** : 401 anonyme, indicateurs exacts, isolation entre utilisateurs, filtre de période appliqué et restitué dans `period`, bornes inclusives, 400 sur date invalide, forme des recentes et du payload global, répartition par type.
- **`api/test_schema.py (1)`** : génération du schéma sous contrainte `fail_on_warn` + présence des chemins `/api/v1/` et de la documentation `client_uuid`/409.

### Exécutés

```
.venv/Scripts/python.exe -m pytest                  → 109 passed (47 web + 38 séances/chevaux + 15 services + 8 dashboard + 1 schéma)
.venv/Scripts/python.exe manage.py check            → aucun problème
.venv/Scripts/python.exe manage.py spectacular --fail-on-warn → 0 erreur, 0 warning
```

Rendu web : inchangé (12/12 tests dashboard existants sans modification des assertions).

## 7. Points d'attention et limites

1. Les **mois multi-années sont agrégés** dans l'affichage mensuel si la période traverse plusieurs années (comportement web conservé à l'identique). À arbitrer produit pour le mobile (lot 09) : tracer les mois par année ou changer de granularité.
2. `total_horses` n'est **pas filtré** par la période (comportement web existant) : le dashboard compte tous les équidés du propriétaire, même exploités hors période.
3. `sessions_dates` du dashboard contient **toutes les séances de la période** (comme le web) ; si un utilisateur accumule des milliers de séances, prévoir une pagination ou un lissage au lot mobile/côté API.
4. SwaggerUI est désactivée en prod via `API_SERVE_DOCS=False` ; le schéma machine-readable reste exposé — il ne contient aucune donnée utilisateur, mais son accessibilité peut être restreinte si la sécurité le demande.
5. Hors périmètre respecté : graphiques natifs React Native, cache SQLite, modification visuelle du site web.

## Fichiers modifiés

| Fichier | Type | Description |
|---|---|---|
| `training/services.py` | ✨ Nouveau | Calculs dashboard partagés web/mobile |
| `training/views.py` | ⚡ Modifié | Vue `dashboard` déléguée au service (rendu inchangé) |
| `training/tests/test_services.py` | ✨ Nouveau | 15 tests unitaires de calculs |
| `api/serializers.py` | ⚡ Modifié | Schémas dashboard (+ `ApiErrorSerializer`, `IdempotencyConflictSerializer` pour OpenAPI) |
| `api/views.py` | ⚡ Modifié | `DashboardView` + annotations `extend_schema` sur tous les endpoints |
| `api/urls.py` / `la_mulerie_training/urls.py` | ⚡ Modifié | `/api/v1/dashboard/`, `/api/schema/`, `/api/docs/` |
| `la_mulerie_training/settings/*.py` | ⚡ Modifié | `drf_spectacular`, `SPECTACULAR_SETTINGS`, `API_SERVE_DOCS` |
| `api/test_schema.py` / `api/test_api.py` | ✨ Nouveau | Tests de schéma (2) et dashboard (9) |
| `requirements.txt` | ⚡ Modifié | Ajout `drf-spectacular==0.30.0` |
| `docs/la-mulerie-mobile-roadmap/05-api-dashboard-et-openapi-RAPPORT.md` | ✨ Nouveau | Ce rapport |

**Prochaine étape :** Lot 06 — application Expo.
