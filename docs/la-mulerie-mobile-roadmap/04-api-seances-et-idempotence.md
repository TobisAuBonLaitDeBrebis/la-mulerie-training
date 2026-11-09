# Lot 04 — API des séances et création idempotente

**Dépendances :** lots 02 et 03.  
**But :** exposer les séances et permettre au mobile d'envoyer plusieurs fois la même création sans créer de doublon.

## Objectif MVP

- consulter les séances accessibles ;
- créer une séance en ligne ;
- accepter un UUID client stable fourni par le mobile ;
- garantir l'idempotence d'une création rejouée après une coupure réseau.

Les modifications/suppressions offline de séances déjà synchronisées sont hors périmètre.

## Analyse préalable obligatoire

- Lire le modèle exact et les formulaires de séance.
- Confirmer la signification de `cavalier`, propriétaire, créateur et équidé associé.
- Vérifier les champs de date/heure, durée, coût, type et notes.
- Vérifier les règles de validation, les valeurs autorisées et les calculs.
- Décider avec le métier quelle relation identifie l'acteur créateur. Ne pas déduire cette règle du seul nom d'un champ.

## Contrat API attendu

Créer au minimum :

- `GET /api/v1/sessions/` : liste des séances autorisées, paginée ;
- `GET /api/v1/sessions/{id}/` : détail autorisé ;
- `POST /api/v1/sessions/` : création validée côté serveur.

Filtres possibles à ajouter si utiles : équidé, date de début, date de fin. Les formats doivent être documentés et validés.

Le payload ne doit pas permettre au client de choisir librement un utilisateur ou de s'approprier un cheval. La relation à l'utilisateur est définie par le serveur à partir de l'identité authentifiée et des règles métier.

## Idempotence

Chaque séance créée sur mobile possède un UUID client généré avant l'envoi. Conserver le même UUID lors de chaque retry.

L'agent doit choisir la mise en œuvre la plus simple compatible avec le modèle réel :

- champ UUID client avec contrainte d'unicité correctement scopée par l'utilisateur/acteur ; ou
- table dédiée d'opérations/idempotency keys si le modèle métier ne permet pas une contrainte sûre.

Ne pas utiliser une contrainte globale non scopée si plusieurs utilisateurs peuvent générer des UUID dans des contextes différents, et ne pas rendre nullable une clé unique sans comprendre les règles SQL/Django concernées.

Comportement requis :

1. Premier POST avec UUID `K` et payload valide : créer la séance et enregistrer l'association de `K` à cette création dans la même transaction.
2. Même utilisateur, même UUID et même contenu : retourner la séance déjà créée avec une réponse de succès cohérente, sans doublon.
3. Même utilisateur et même UUID avec contenu différent : retourner un conflit explicite (HTTP 409 recommandé), sans écraser silencieusement la séance.
4. UUID déjà utilisé par un autre utilisateur : aucune fuite ni accès à la séance d'autrui.
5. Erreur de validation : réponse 400 structurée, sans enregistrer une séance partielle.

L'enregistrement de l'idempotency key et la création doivent être atomiques (`transaction.atomic`) et protégés par la contrainte de base de données. Gérer proprement les collisions concurrentes.

## Dates et valeurs

- Conserver exactement la sémantique actuelle des dates/heures et du fuseau horaire.
- Ne pas convertir arbitrairement une date locale en UTC ni l'inverse.
- Conserver les unités de durée et de coût existantes ; documenter les unités dans le schéma OpenAPI.
- Valider que l'équidé référencé est accessible à l'utilisateur.

## Tests requis

- création valide ;
- champs absents/invalides ;
- cheval inaccessible ;
- utilisateur anonyme ;
- liste et détail filtrés par utilisateur ;
- même UUID / même payload ne crée qu'une séance ;
- même UUID / payload différent retourne un conflit ;
- deux requêtes concurrentes ne créent pas de doublon ;
- migration et données historiques compatibles ;
- parcours web et formulaires inchangés.

## Hors périmètre

- édition/suppression offline ;
- création de séance sans identité de compte préalable ;
- synchronisation locale ;
- pièces jointes ou upload de fichiers.

## Critères d'acceptation

- [ ] Liste, détail et création sont disponibles.
- [ ] Autorisations et validations reprennent les règles métier existantes.
- [ ] La création est idempotente avec un UUID client stable.
- [ ] Les collisions et conflits sont testés.
- [ ] Les tests de régression web passent.
