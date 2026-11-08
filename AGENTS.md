# AGENTS.md — La Mulerie Training

## 1. Présentation du projet

La Mulerie Training est une application web permettant de centraliser le suivi et l'analyse des entraînements des équidés (mules, chevaux, etc.).

Les objectifs principaux sont :
- Gérer les équidés.
- Enregistrer et consulter les séances d'entraînement.
- Centraliser les données d'activité.
- Produire des statistiques et des graphiques.
- Proposer une interface simple, responsive et agréable à utiliser.

### Stack technique

- **Backend :** Python / Django.
- **Frontend :** Tailwind CSS / DaisyUI.
- **Interactions dynamiques :** HTMX.
- **Tests :** respecter l'outillage déjà configuré dans le dépôt, notamment `pytest.ini`.

### Organisation actuelle

Le dépôt contient notamment les applications et dossiers suivants :

- `accounts/` : gestion des comptes utilisateurs.
- `training/` : fonctionnalités liées aux entraînements.
- `la_mulerie_training/` : configuration principale Django.
- `theme/` : éléments liés au thème et au frontend.

Cette organisation peut évoluer, mais toute évolution doit être justifiée et cohérente avec les responsabilités de chaque application.

---

## 2. Règle fondamentale : comprendre avant de coder

Avant toute modification :

1. Lire le README et ce fichier AGENTS.md.
2. Explorer l'architecture existante.
3. Identifier les applications Django concernées.
4. Examiner les modèles, vues, formulaires, URLs et templates concernés.
5. Consulter les tests existants.
6. Comprendre les conventions déjà utilisées.
7. Identifier les éventuels effets de bord.

Ne jamais modifier du code sans avoir compris son rôle dans l'application.

Ne pas réécrire une fonctionnalité existante sans raison valable.

Ne pas inventer de règles métier. En cas de doute, demander une clarification.

---

## 3. Qualité du code : Clean Code

La qualité et la maintenabilité du code sont des priorités absolues.

Respecter les principes suivants :

- Écrire du code simple, lisible et explicite.
- Utiliser des noms de variables, fonctions et classes compréhensibles.
- Limiter la taille des fonctions et leur nombre de responsabilités.
- Éviter les imbrications conditionnelles excessives.
- Éviter les effets de bord.
- Éviter les valeurs magiques.
- Supprimer les imports inutilisés et le code mort.
- Ajouter des commentaires uniquement lorsqu'ils apportent une réelle explication.
- Respecter les conventions Python (PEP 8) et Django.

Privilégier systématiquement la lisibilité à l'ingéniosité.

Un développeur doit pouvoir comprendre rapidement le rôle d'un composant sans devoir analyser toute l'application.

---

## 4. Architecture : SOLID et séparation des responsabilités

Appliquer les principes SOLID de manière pragmatique.

### Single Responsibility Principle

Chaque classe, fonction ou module doit avoir une responsabilité clairement identifiée.

Éviter notamment :
- Les vues Django contenant toute la logique métier.
- Les modèles contenant des responsabilités sans rapport avec leur domaine.
- Les fonctions qui effectuent trop d'opérations différentes.

### Open/Closed Principle

Privilégier les extensions propres plutôt que les modifications répétées de fonctionnalités existantes.

### Dependency Inversion Principle

Éviter les dépendances inutilement fortes entre les différentes parties de l'application.

### Architecture Django

Respecter les responsabilités habituelles :

- Models : données, relations et règles directement liées aux entités.
- Views : orchestration des requêtes HTTP.
- Forms : validation et traitement des données utilisateur.
- Services : logique métier complexe ou réutilisable lorsqu'une séparation est justifiée.
- Selectors ou QuerySets : requêtes de lecture complexes lorsqu'une abstraction est utile.
- Templates : présentation des données.

Ne pas multiplier artificiellement les couches ou les abstractions.

L'objectif est une architecture simple, évolutive et compréhensible.

---

## 5. DRY — Don't Repeat Yourself

La duplication de code doit être évitée.

Avant d'implémenter une fonctionnalité :

1. Vérifier si une logique similaire existe déjà.
2. Identifier les composants réutilisables.
3. Factoriser les traitements réellement communs.
4. Centraliser les règles métier partagées.

Utiliser les mécanismes Django appropriés :

- Fonctions et méthodes partagées.
- Managers et QuerySets personnalisés.
- Formulaires réutilisables.
- Mixins lorsque cela apporte une réelle valeur.
- Templates inclus.
- Template tags et filtres personnalisés si nécessaire.

Attention : DRY ne signifie pas créer des abstractions pour chaque ligne de code répétée.

Une abstraction doit simplifier la maintenance, pas la compliquer.

---

## 6. Tests automatisés : une priorité absolue

Les tests font partie intégrante de chaque développement.

**Toute nouvelle fonctionnalité ou correction de bug doit être accompagnée de tests pertinents dans la mesure du possible.**

Ne jamais considérer une tâche comme terminée simplement parce que le code fonctionne manuellement.

### Types de tests à privilégier

**Tests unitaires**
- Fonctions métier.
- Calculs.
- Validations.
- Méthodes des modèles.

**Tests d'intégration**
- Interaction entre applications Django.
- Relations entre modèles.
- Parcours fonctionnels complets.

**Tests de vues**
- Codes HTTP.
- Redirections.
- Permissions.
- Utilisateurs authentifiés et non authentifiés.
- Réponses HTMX.

**Tests de formulaires**
- Données valides.
- Données invalides.
- Champs obligatoires.
- Cas limites.

**Tests de régression**
- Vérifier qu'une correction ne casse pas une fonctionnalité existante.

### Exigences

- Ajouter des tests pour chaque nouveau comportement.
- Couvrir les cas nominaux et les cas d'erreur.
- Tester les permissions et les accès aux données.
- Tester les règles métier importantes.
- Éviter les tests dépendants de l'ordre d'exécution.
- Réutiliser les fixtures et factories lorsqu'elles sont pertinentes.
- Ne jamais supprimer un test simplement parce qu'il échoue.
- Ne jamais modifier les assertions pour masquer une régression.

Privilégier une couverture de tests aussi élevée que raisonnablement possible, en accordant une attention particulière à la logique métier.

Ne pas rechercher uniquement un pourcentage de couverture : la pertinence des tests est essentielle.

### Avant chaque livraison

Exécuter :
1. Les tests liés aux fonctionnalités modifiées.
2. La suite complète de tests.
3. Les vérifications de qualité disponibles.
4. Les vérifications Django adaptées, notamment `python manage.py check`.

Signaler clairement les tests qui n'ont pas pu être exécutés.

---

## 7. Bonnes pratiques Django

Respecter les conventions et mécanismes natifs de Django.

- Utiliser l'ORM Django.
- Utiliser les formulaires Django pour les validations adaptées.
- Protéger les vues avec les permissions nécessaires.
- Éviter les requêtes N+1 avec `select_related` et `prefetch_related`.
- Éviter les requêtes inutiles.
- Utiliser les transactions lorsque plusieurs opérations doivent être atomiques.
- Respecter les contraintes d'intégrité de la base de données.
- Utiliser les migrations Django pour toute modification de schéma.
- Ne jamais modifier arbitrairement une migration déjà appliquée.
- Éviter de placer des traitements complexes directement dans les templates.

Toute modification des modèles doit être accompagnée des migrations nécessaires et de tests adaptés.

---

## 8. Sécurité

La sécurité doit être prise en compte dès la conception.

- Ne jamais stocker de secrets dans le dépôt.
- Ne jamais exposer de mots de passe ou tokens dans les logs.
- Ne jamais désactiver CSRF pour contourner un problème.
- Vérifier les permissions côté serveur.
- Ne jamais faire confiance aux données transmises par le navigateur.
- Prévenir les injections SQL en utilisant correctement l'ORM.
- Éviter les contenus HTML non échappés.
- Vérifier les droits d'accès aux données appartenant à chaque utilisateur.
- Ne pas exposer de données personnelles inutilement.

Masquer un bouton dans l'interface ne constitue jamais une protection suffisante.

---

## 9. Frontend : Tailwind CSS, DaisyUI et HTMX

Respecter les technologies et conventions déjà présentes.

### Tailwind et DaisyUI

- Réutiliser les composants existants.
- Maintenir une cohérence graphique.
- Favoriser les composants réutilisables.
- Éviter la duplication de structures HTML.
- Construire une interface responsive.
- Prendre en compte l'accessibilité.

### HTMX

- Garder les interactions prévisibles.
- Utiliser des endpoints Django cohérents.
- Gérer correctement les réponses HTTP.
- Prévoir les états d'erreur.
- Éviter de dupliquer la logique métier côté frontend.
- Conserver les validations importantes côté serveur.

L'interface doit rester utilisable sans complexifier inutilement l'architecture backend.

---

## 10. Gestion des données d'entraînement

Les données liées aux équidés et à leurs entraînements constituent le cœur métier de l'application.

Toute évolution doit préserver leur cohérence.

Porter une attention particulière :
- Aux relations entre équidés et séances.
- À la cohérence des dates et horaires.
- Aux unités de mesure.
- Aux éventuelles valeurs manquantes.
- Aux calculs de statistiques.
- À la fiabilité des données historiques.

Les calculs métier doivent être centralisés et testés.

Éviter de reproduire les mêmes calculs dans plusieurs vues ou templates.

Ne jamais supprimer ou transformer des données historiques sans comprendre les conséquences fonctionnelles.

---

## 11. Dépendances et maintenabilité

Avant d'ajouter une bibliothèque :

1. Vérifier si une solution existe déjà.
2. Vérifier la compatibilité avec le projet.
3. Vérifier la maintenance de la bibliothèque.
4. Évaluer son intérêt réel.

Éviter les dépendances inutiles.

Ne pas modifier les versions des dépendances sans nécessité.

Documenter les nouvelles configurations et variables d'environnement.

---

## 12. Méthode de travail obligatoire

Pour chaque demande, suivre ce processus :

### Étape 1 — Analyse

Comprendre le besoin et identifier les composants concernés.

### Étape 2 — Exploration

Lire le code existant et les tests associés.

### Étape 3 — Conception

Définir une solution simple, maintenable et cohérente avec l'architecture.

Identifier les tests nécessaires avant de coder.

### Étape 4 — Implémentation

Développer progressivement en respectant Clean Code, SOLID et DRY.

### Étape 5 — Tests

Ajouter les tests nécessaires et exécuter les vérifications.

### Étape 6 — Relecture

Vérifier :
- La lisibilité.
- La duplication.
- Les responsabilités.
- La sécurité.
- Les éventuels effets de bord.
- Les performances.
- Les régressions possibles.

### Étape 7 — Documentation

Actualiser la documentation si nécessaire.

---

## 13. Ce qu'il ne faut jamais faire

- Implémenter une fonctionnalité sans comprendre l'existant.
- Dupliquer une logique métier déjà présente.
- Ajouter des abstractions inutiles.
- Introduire des dépendances sans justification.
- Ignorer les erreurs des tests.
- Supprimer des tests pour faire passer une suite.
- Contourner les validations ou permissions.
- Modifier des données sans comprendre leur structure.
- Faire des refactorisations massives hors périmètre.
- Modifier des fichiers sans rapport avec la tâche.
- Effectuer des commits, pushes ou déploiements sans demande explicite.
- Lancer des commandes destructives sans autorisation.

---

## 14. Définition d'une tâche terminée

Une tâche est terminée uniquement lorsque :

- La fonctionnalité demandée est implémentée.
- Le code est lisible et maintenable.
- Les responsabilités sont correctement séparées.
- Les duplications inutiles ont été évitées.
- Les tests pertinents ont été créés ou adaptés.
- Les tests ont été exécutés autant que possible.
- Les éventuelles migrations sont présentes.
- Les permissions et la sécurité sont respectées.
- La documentation est actualisée si nécessaire.

Ne jamais déclarer une tâche terminée si des problèmes connus restent non signalés.

---

## 15. Compte rendu obligatoire

À la fin de chaque intervention, fournir un compte rendu contenant :

### Résumé
Description des changements réalisés.

### Fichiers modifiés
Liste des principaux fichiers concernés.

### Tests
- Tests ajoutés.
- Tests modifiés.
- Commandes exécutées.
- Résultats obtenus.

### Points d'attention
- Problèmes rencontrés.
- Hypothèses prises.
- Limites éventuelles.
- Actions restant à effectuer.

Ne jamais prétendre avoir exécuté une commande ou un test qui ne l'a pas été.

---

## Principe directeur

**La qualité du code est plus importante que la vitesse de développement.**

Chaque modification doit contribuer à construire une application fiable, simple à comprendre, facile à faire évoluer et agréable à maintenir.

Privilégier systématiquement :

1. La simplicité.
2. La lisibilité.
3. La séparation des responsabilités.
4. La réutilisation pertinente du code (DRY).
5. Les tests automatisés.
6. La sécurité.
7. La maintenabilité à long terme.

Agis comme un développeur senior responsable de la qualité technique du projet, et pas simplement comme un générateur de code.