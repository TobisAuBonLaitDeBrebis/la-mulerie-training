# Lot 07 — SQLite et repositories locaux

**Dépendance :** lot 06.  
**But :** rendre les données disponibles localement et fournir aux écrans une interface de données indépendante du réseau.

## Objectif

Créer une base SQLite locale versionnée, des migrations et des repositories typés. À la fin de ce lot, l'application peut lire/écrire des données locales de test, mais la synchronisation distante complète est traitée au lot 08.

## Technologie

Utiliser `expo-sqlite` compatible avec la version Expo installée. Vérifier la documentation officielle et les API réellement disponibles ; ne pas copier des méthodes d'une autre version.

## Schéma local de départ

Adapter les colonnes aux champs réels confirmés dans Django et OpenAPI. Les exemples ci-dessous sont conceptuels :

### `local_horses`

- `local_id` : identifiant local stable, texte/UUID ;
- `server_id` : identifiant serveur, nullable ;
- `account_id` : identifiant de compte propriétaire du cache ;
- champs métier nécessaires à l'affichage ;
- `server_updated_at` ou `updated_at` si défini par le contrat.

### `local_training_sessions`

- `local_id` : UUID client, clé primaire ;
- `server_id` : identifiant serveur nullable ;
- `account_id` ;
- `horse_local_id` et/ou `horse_server_id` selon la stratégie de relation retenue ;
- champs de séance conformes au contrat ;
- `sync_status` ;
- `created_local_at`, `updated_local_at`.

### `sync_outbox`

- `operation_id` : UUID stable ;
- `account_id` ;
- `entity_type` ;
- `entity_local_id` ;
- `operation` ;
- `payload` JSON sérialisé et versionné ;
- `status` (`pending`, `in_progress`, `failed` ou états justifiés) ;
- `attempts`, `last_error`, `created_at`, `next_attempt_at`.

### `local_sync_state`

- compte ;
- dernier snapshot complet ;
- curseur éventuel si le protocole delta est retenu ;
- informations de version de schéma/protocole nécessaires.

Éviter de stocker le même payload dans plusieurs colonnes sans nécessité. Ne stocker ni mot de passe ni jeton dans SQLite.

## Implémentation

1. Mettre en place l'ouverture de base et les migrations SQL numérotées.
2. Utiliser les transactions pour les opérations multi-tables.
3. Activer les contraintes d'intégrité (dont clés étrangères) de manière vérifiée.
4. Créer des repositories dédiés aux équidés et séances.
5. Exposer des méthodes métier claires (`list`, `get`, `upsertFromServer`, `createLocal`, etc.) et éviter de faire des requêtes SQL dans les composants UI.
6. Utiliser des requêtes paramétrées ; jamais de concaténation de valeurs utilisateur dans SQL.
7. Prévoir les index utiles à partir des requêtes réellement exécutées.
8. Ajouter des tests de migration et de repository.

## Isolation par compte

Toutes les requêtes de lecture/écriture locales doivent être scopées par le compte actif. Les identifiants locaux d'un compte ne doivent pas être visibles dans un autre espace utilisateur.

À la déconnexion :

- ne pas effacer silencieusement les opérations non synchronisées ;
- les conserver attachées à leur `account_id` ;
- ne jamais les transmettre au prochain compte connecté ;
- prévoir un message utilisateur clair si des opérations restent en attente.

## Données de test

Les repositories doivent permettre de tester la base avec des données factices sans accès réseau. Ajouter des tests pour le redémarrage/réouverture de la base et la persistance.

## Hors périmètre

- envoi réel de l'outbox ;
- écrans finaux ;
- modification/suppression offline de données synchronisées ;
- chiffrement SQLite implicite. Si un chiffrement local est requis, faire une décision séparée.

## Critères d'acceptation

- [ ] Schéma SQLite documenté et migrations versionnées.
- [ ] Repositories typés pour chevaux et séances.
- [ ] Écritures multi-tables atomiques.
- [ ] Données persistantes après fermeture/réouverture.
- [ ] Isolation entre comptes testée.
- [ ] Aucun secret ou token n'est stocké dans SQLite.
