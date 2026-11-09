# Lot 00 — Audit et état initial

**Type :** audit sans refactorisation fonctionnelle.  
**But :** établir l'état réel du dépôt avant de toucher au code.

## Objectif

Comprendre la structure actuelle de La Mulerie Training, identifier les règles métier existantes et disposer d'une référence fiable pour les tests et le fonctionnement du site web.

Le dépôt contient actuellement les domaines `accounts/`, `training/`, la configuration `la_mulerie_training/` et le dossier frontend `theme/`. Le README présente Django, Tailwind CSS, DaisyUI et HTMX. Vérifier ces informations dans l'état actuel du checkout plutôt que de supposer qu'elles sont toujours exactes.

## Instructions à l'agent

1. Lire intégralement `AGENTS.md`, `README.md`, `requirements.txt` et `pytest.ini`.
2. Relever l'arborescence réelle et la configuration Django active (settings, URLs, middleware, apps installées, base de données).
3. Examiner les modèles, migrations, vues, formulaires, URLs, templates et tests de `accounts/` et `training/`.
4. Identifier les relations exactes entre `User`, équidés et séances. Noter le sens métier de chaque relation (`proprietaire`, `cavalier`, créateur, partage éventuel).
5. Identifier les champs de date/heure, durées, coûts, unités et règles de calcul.
6. Repérer les vues qui réalisent des calculs réutilisables, en particulier le tableau de bord/statistiques.
7. Vérifier comment les suppressions, modifications et filtres par utilisateur fonctionnent côté web.
8. Lancer les vérifications existantes sans modifier le comportement : tests, `python manage.py check`, et autres commandes déjà documentées.
9. Signaler les tests manquants ou les erreurs préexistantes sans les corriger dans ce lot.

## Livrables attendus

Créer ou mettre à jour `docs/roadmap-mobile/ETAT-INITIAL.md` avec :

- versions réelles de Python et Django et dépendances pertinentes ;
- applications et chemins importants ;
- modèles, champs et relations exacts ;
- règles d'accès déduites du code et règles métier encore ambiguës ;
- routes web existantes à préserver ;
- tests et commandes disponibles ;
- résultats des tests de référence ;
- risques / décisions humaines nécessaires avant le lot 01.

Ne pas recopier de secrets, données personnelles ou valeurs de `.env` dans ce rapport.

## Hors périmètre

- aucune modification de modèle ;
- aucune migration ;
- aucune installation de dépendance ;
- aucun déplacement massif de fichiers ;
- aucune API ;
- aucune application mobile.

## Critères d'acceptation

- [ ] `AGENTS.md` et la documentation existante ont été lus.
- [ ] Les modèles et règles d'accès sont documentés à partir du code réel.
- [ ] Les tests de référence ont été exécutés ou leur impossibilité est expliquée.
- [ ] `ETAT-INITIAL.md` distingue faits vérifiés, hypothèses et questions métier.
- [ ] Aucun comportement applicatif n'a été changé.

## Compte rendu

Utiliser le format obligatoire de `AGENTS.md`. Ne pas passer au lot 01 si une décision de propriété des données est nécessaire et non résolue.
