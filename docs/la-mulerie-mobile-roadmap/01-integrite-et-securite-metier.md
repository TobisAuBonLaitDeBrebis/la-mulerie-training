# Lot 01 — Intégrité et sécurité métier

**Dépendance :** lot 00 terminé.  
**But :** garantir que les relations entre comptes, équidés et séances sont cohérentes avant de les exposer à une API.

## Objectif

Sécuriser les opérations déjà présentes dans l'application web et clarifier les règles d'accès. Préserver les données existantes et éviter toute migration destructive.

## Analyse préalable obligatoire

S'appuyer sur `ETAT-INITIAL.md` et revérifier le code concerné.

- Identifier le modèle utilisateur réel (`AUTH_USER_MODEL` compris).
- Identifier les relations entre l'utilisateur, le propriétaire de l'équidé, le cavalier et la séance.
- Déterminer si un compte peut consulter les chevaux d'un autre compte, s'il existe des partages, et qui peut créer/modifier/supprimer une séance.
- Examiner les données historiques qui ne respecteraient pas les contraintes envisagées (`NULL`, objets orphelins, relations incohérentes).

**Ne pas inventer la règle métier.** Si les notions de propriétaire, cavalier et créateur ne permettent pas de conclure aux droits, produire une question précise et arrêter uniquement la modification correspondante jusqu'à décision.

## Travaux demandés

### A. Suppressions web

- Vérifier les vues de suppression des équidés et séances.
- Une suppression déclenchée par le navigateur doit utiliser une méthode non sûre adaptée, normalement POST dans le formulaire Django, protégée par CSRF.
- Refuser GET pour toute suppression (réponse 405 ou comportement Django cohérent).
- Vérifier les permissions sur l'objet avant suppression.
- Conserver les pages de confirmation et le parcours web existant autant que possible.

### B. Filtrage et propriété

- Centraliser uniquement les filtres réellement partagés si nécessaire.
- Toute vue de détail, modification ou suppression doit filtrer l'objet selon les règles d'accès établies.
- Ne jamais se fier à un identifiant d'objet fourni par l'interface sans vérifier le droit d'accès.
- Toute relation envoyée par le client doit être validée côté serveur.

### C. Contraintes de modèles

- Ne rendre un champ obligatoire (`null=False`, `blank=False`) qu'après vérification de la règle métier et de toutes les données existantes.
- Si des données historiques sont incomplètes, proposer une migration de données réversible ou un plan de nettoyage explicite ; ne pas inventer une valeur.
- Ajouter des contraintes `UniqueConstraint`, `CheckConstraint` ou index seulement si une invariance métier vérifiée le justifie.
- Corriger les valeurs par défaut incohérentes (par exemple date vs datetime) uniquement après vérification des usages et avec tests.

### D. Tests

Ajouter des tests pour :

- accès autorisé et refusé à un objet ;
- tentative d'accès à un objet d'un autre utilisateur ;
- méthode GET refusée pour une suppression ;
- suppression autorisée selon les règles métier ;
- données historiques et cas `NULL` pertinents ;
- non-régression des parcours web existants.

## Contraintes d'implémentation

- Conserver les templates Django, Tailwind, DaisyUI et HTMX.
- Éviter une refactorisation générale des vues.
- Ne pas modifier des migrations déjà appliquées.
- Examiner les migrations générées avant de les conserver.
- Toute migration doit être testée sur une base de test représentative.

## Hors périmètre

- installation de DRF ;
- endpoints API ;
- JWT ;
- mobile et SQLite.

## Critères d'acceptation

- [ ] Règles de propriété et d'accès documentées.
- [ ] Aucun GET ne peut supprimer une donnée.
- [ ] Les accès aux objets sont filtrés côté serveur.
- [ ] Les migrations sont sûres et n'inventent aucune donnée.
- [ ] Les tests web et métier passent.
- [ ] `python manage.py check` passe.
- [ ] L'interface web reste fonctionnelle.
