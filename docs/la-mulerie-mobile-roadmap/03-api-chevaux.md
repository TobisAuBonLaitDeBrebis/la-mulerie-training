# Lot 03 — API des équidés

**Dépendances :** lots 01 et 02.  
**But :** permettre au mobile de consulter les équidés accessibles à l'utilisateur connecté.

## Objectif MVP

Exposer la liste et le détail des équidés, avec pagination si nécessaire. La création, modification et suppression depuis le mobile peuvent rester hors périmètre initial ; ne les ajouter que si l'interface produit les exige.

## Analyse préalable

- Vérifier le modèle exact, ses champs, relations, propriétés calculées et contraintes.
- Vérifier les formulaires et vues web existants pour comprendre les validations.
- Établir les règles d'accès à partir du lot 01 : propriétaire, cavaliers autorisés, éventuel partage.
- Identifier les données qu'il est utile de mettre en cache hors ligne.

## Implémentation

### A. Sérialisation

Créer un serializer dédié à la lecture mobile. Ne pas exposer automatiquement tous les champs du modèle.

Inclure uniquement les champs nécessaires aux écrans mobiles, par exemple :

- identifiant serveur ;
- nom ;
- race si présente ;
- date de naissance si présente ;
- propriétaire ou information de partage uniquement si utile et autorisé ;
- `updated_at` si le modèle le permet et si sa sémantique est fiable.

Respecter les vrais noms/types de champs du projet. Les exemples ci-dessus ne constituent pas une demande de renommer les modèles.

### B. Endpoints

Créer au minimum :

- `GET /api/v1/horses/` : liste filtrée selon les droits de l'utilisateur ;
- `GET /api/v1/horses/{id}/` : détail d'un équidé accessible.

Utiliser la pagination DRF. La taille de page doit être raisonnable et documentée. Les filtres supplémentaires ne doivent être ajoutés qu'en fonction d'un besoin concret.

### C. Permissions

- L'ensemble de la queryset est filtré selon l'utilisateur authentifié et la règle d'accès validée au lot 01.
- Le détail d'un objet inaccessible doit être refusé sans révéler son existence à un compte non autorisé (404 est souvent préférable pour une ressource filtrée).
- Ne jamais accepter un propriétaire fourni par le client pour contourner les règles d'accès.
- Toute future mutation devra dériver le propriétaire/acteur côté serveur.

### D. Réutilisation du métier

Si la lecture nécessite une requête complexe partagée, utiliser un selector ou un QuerySet adapté. Ne pas créer une couche d'abstraction si une queryset claire suffit.

## Tests requis

- liste vide et liste avec plusieurs chevaux ;
- pagination ;
- champs exposés exactement ;
- utilisateur anonyme refusé ;
- un utilisateur ne voit pas les chevaux non autorisés ;
- accès au détail autorisé/refusé ;
- aucune régression des vues/templates web.

## Hors périmètre

- création de cheval hors ligne ;
- synchronisation SQLite ;
- écriture mobile non requise par le MVP.

## Critères d'acceptation

- [ ] Liste et détail documentés et testés.
- [ ] Les droits sont appliqués au niveau queryset et objet.
- [ ] Le serializer n'expose pas de champs inutiles ou sensibles.
- [ ] Pagination et format JSON sont stables.
- [ ] Les parcours web restent fonctionnels.
