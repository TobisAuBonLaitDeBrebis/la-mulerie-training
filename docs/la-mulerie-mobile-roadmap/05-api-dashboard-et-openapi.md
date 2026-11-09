# Lot 05 — Dashboard API et contrat OpenAPI

**Dépendances :** lots 03 et 04.  
**But :** fournir les données du tableau de bord mobile et documenter précisément l'API.

## Objectif

Réutiliser les mêmes calculs que le tableau de bord web, puis exposer une réponse JSON stable. Ajouter une documentation OpenAPI exploitable pour le développement mobile et la génération éventuelle de types TypeScript.

## Partie A — Calculs métier

1. Examiner la vue dashboard actuelle et ses requêtes.
2. Inventorier chaque indicateur réellement affiché (coûts, durées, moyennes, répartition des séances, évolution mensuelle, calendrier, etc.).
3. Identifier les filtres, périodes, règles d'arrondi, exclusions, fuseaux horaires et valeurs manquantes.
4. Extraire uniquement les calculs réutilisables dans une fonction/service ou selector clairement nommé.
5. Faire appeler ce composant commun par la vue web, sans changer le rendu ni les résultats.
6. Ajouter des tests unitaires sur les calculs avant de les exposer à l'API.

Ne pas calculer les mêmes indicateurs indépendamment dans Django et React Native.

## Partie B — Endpoint

Créer `GET /api/v1/dashboard/` qui :

- exige un utilisateur authentifié ;
- ne calcule que sur les données auxquelles cet utilisateur a droit ;
- accepte uniquement les filtres de période réellement utiles ;
- retourne une structure JSON typée, documentée et stable ;
- évite de retourner des objets Django ou des champs internes bruts.

Si les données nécessaires sont volumineuses, mesurer le coût et appliquer agrégations/pagination adaptées avant toute optimisation prématurée.

## Partie C — OpenAPI

Ajouter un générateur OpenAPI compatible avec la version DRF/Django installée (par exemple `drf-spectacular`, après vérification de compatibilité).

- Documenter tous les endpoints `/api/v1/`.
- Décrire authentification, paramètres, pagination, schémas, formats de date, unités et codes d'erreur.
- Documenter explicitement l'UUID client et le comportement 409 du POST des séances.
- Ajouter les schémas de réponses 401, 403/404, 400, 409 et 5xx utiles.
- Exposer le schéma et une interface Swagger/ReDoc uniquement selon les règles d'accès appropriées à chaque environnement.
- Vérifier le schéma généré et corriger les avertissements significatifs.

La génération automatique de types TypeScript est facultative dans ce lot : ne l'ajouter que si elle apporte une valeur et si la commande peut être reproduite dans le dépôt.

## Tests requis

- exactitude des statistiques par rapport au tableau web sur des jeux de données contrôlés ;
- isolation des données entre utilisateurs ;
- périodes limites et fuseaux horaires ;
- tests de l'endpoint dashboard ;
- génération OpenAPI sans erreur ;
- validation du schéma (commande de validation fournie par la bibliothèque).

## Hors périmètre

- graphiques natifs React Native ;
- cache SQLite ;
- modification visuelle du tableau web.

## Critères d'acceptation

- [ ] Les calculs sont partagés entre web et API.
- [ ] Le dashboard mobile retourne les indicateurs nécessaires.
- [ ] Les résultats sont testés et cohérents avec le web.
- [ ] Le schéma OpenAPI décrit les contrats et erreurs.
- [ ] Aucun endpoint n'expose les données d'un autre utilisateur.
