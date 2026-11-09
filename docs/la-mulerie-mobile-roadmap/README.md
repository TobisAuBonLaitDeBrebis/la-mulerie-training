# La Mulerie Training — feuille de route mobile offline-first

Ce dossier contient des lots de travail indépendants à confier à un agent de code, **un par un et dans l'ordre**. L'objectif est de faire évoluer l'application Django existante vers un backend commun au site web et à une application mobile iOS/Android, sans réécriture générale.

## Architecture visée

- **Web existant :** Django Templates, Tailwind CSS, DaisyUI et HTMX. À conserver.
- **Backend commun :** monolithe Django existant, complété par Django REST Framework (DRF).
- **Mobile :** React Native + Expo + TypeScript.
- **Stockage local mobile :** SQLite via `expo-sqlite`.
- **Synchronisation :** file d'attente locale (outbox), API Django idempotente, reprise automatique au retour au premier plan et lorsque le réseau est disponible.
- **Base distante :** conserver la base et l'ORM actuellement configurés dans le dépôt. Ne pas imposer PostgreSQL si le projet n'y est pas déjà configuré.

> Le projet est au début de son développement. Il faut privilégier une architecture simple, progressive et testée. Aucun microservice, aucune réécriture Rust et aucune WebView ne sont nécessaires pour cette feuille de route.

## Ordre d'exécution

| Ordre | Fichier | Objectif | Dépend de |
|---:|---|---|---|
| 0 | `00-audit-et-etat-initial.md` | Auditer l'existant et établir une référence de tests | — |
| 1 | `01-integrite-et-securite-metier.md` | Clarifier et sécuriser les relations et suppressions | 0 |
| 2 | `02-socle-api-authentification.md` | Installer DRF et poser le socle d'API/authentification | 1 |
| 3 | `03-api-chevaux.md` | Exposer les chevaux de l'utilisateur | 2 |
| 4 | `04-api-seances-et-idempotence.md` | Exposer les séances et préparer la création hors ligne | 2, 3 |
| 5 | `05-api-dashboard-et-openapi.md` | Exposer les statistiques et documenter le contrat API | 3, 4 |
| 6 | `06-application-expo.md` | Initialiser l'application mobile | 2 |
| 7 | `07-sqlite-et-repositories.md` | Créer la base locale et la couche d'accès aux données | 6 |
| 8 | `08-synchronisation-offline-first.md` | Implémenter la synchronisation robuste | 3, 4, 7 |
| 9 | `09-ecrans-et-parcours-mobiles.md` | Développer les parcours mobiles sur les données locales | 5, 7, 8 |
| 10 | `10-recette-securite-et-publication.md` | Valider les parcours et préparer une première distribution | 0 à 9 |

Les numéros sont des lots de développement, pas des instructions demandant de tout exécuter automatiquement. L'agent doit traiter uniquement le fichier explicitement demandé par l'utilisateur. Il peut signaler une dépendance manquante, mais ne doit pas enchaîner les lots sans autorisation.

## Consigne à donner à l'agent

Depuis la racine du dépôt, demander par exemple :

> Lis `AGENTS.md` puis `docs/roadmap-mobile/README.md` et `docs/roadmap-mobile/00-audit-et-etat-initial.md`. Réalise uniquement le lot 00. Respecte son périmètre, exécute les tests possibles et rends le compte rendu exigé par `AGENTS.md`. Ne fais aucun commit, push ou déploiement.

Pour le lot suivant, remplacer le nom du fichier. Chaque lot doit se terminer par ses critères d'acceptation avant de commencer le suivant.

## Règles globales non négociables

1. Lire le `AGENTS.md` racine avant toute intervention. Ses règles priment sur ce dossier en cas de contradiction.
2. Explorer le code réel avant de proposer ou modifier des fichiers. Les noms de modèles et champs mentionnés dans les lots sont des points de départ à vérifier, pas une autorisation d'inventer le schéma.
3. Préserver le fonctionnement du site web existant. Toute régression web est un défaut bloquant.
4. Ne pas inventer les règles de propriété/partage des équidés. Si le code ne permet pas de déterminer qui peut consulter ou gérer un cheval ou une séance, documenter le point et demander une décision humaine avant d'appliquer une règle destructive ou trop restrictive.
5. Ajouter des tests à chaque comportement. Ne jamais supprimer ou affaiblir un test pour faire passer la suite.
6. Utiliser des migrations réversibles lorsque c'est possible. Ne jamais modifier une migration déjà appliquée.
7. Ne pas stocker de mots de passe ou de jetons dans SQLite, AsyncStorage, les logs ou le dépôt. Les jetons mobiles doivent utiliser un stockage sécurisé adapté à la plateforme.
8. Les données hors ligne sont isolées par compte utilisateur. Aucune donnée locale en attente ne doit être envoyée au compte d'un autre utilisateur.
9. Toutes les mutations hors ligne doivent être idempotentes côté serveur. Une relance réseau ne doit jamais créer un doublon.
10. Ne pas prétendre qu'une synchronisation en arrière-plan sera exécutée à une heure précise : iOS et Android contrôlent le calendrier des tâches en arrière-plan.
11. Vérifier la compatibilité des dépendances avec les versions réellement présentes et la documentation officielle actuelle avant de les ajouter. Ne pas figer des versions anciennes trouvées dans un exemple.
12. Ne pas réaliser de commit, push, publication sur les stores ou déploiement sans demande explicite.

## Décisions de périmètre pour le premier MVP

- Le premier parcours offline prioritaire est : **consulter les chevaux déjà synchronisés, consulter l'historique déjà synchronisé, créer une séance hors ligne, puis la synchroniser**.
- La modification et la suppression hors ligne d'une séance déjà synchronisée ne font pas partie du premier MVP. Elles pourront être ajoutées après définition d'une stratégie de conflits et de suppressions différées.
- La création d'un cheval peut rester en ligne dans le premier MVP, sauf si le produit exige explicitement cette fonction hors ligne.
- Les tableaux de bord hors ligne sont calculés à partir des données locales disponibles et doivent être identifiés comme tels si la synchronisation n'est pas à jour.
- Le web reste utilisable indépendamment de l'application mobile.
- Une première synchronisation complète paginée est acceptable pour le petit volume initial. Ne mettre en place un protocole delta complexe que si le volume ou les besoins le justifient.

## Compte rendu attendu de chaque lot

À la fin de chaque lot, l'agent doit fournir :

- résumé des changements ;
- fichiers créés/modifiés ;
- migrations éventuelles ;
- tests ajoutés et commandes exécutées ;
- résultats exacts des tests ;
- hypothèses et décisions métier nécessitant validation ;
- limites connues et prochain lot recommandé.
