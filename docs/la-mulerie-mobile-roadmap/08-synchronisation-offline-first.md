# Lot 08 — Synchronisation offline-first

**Dépendances :** API chevaux (03), API séances/idempotence (04) et repositories SQLite (07).  
**But :** permettre de créer une séance sans réseau puis de la retrouver côté web après synchronisation.

## Objectif MVP

Le premier périmètre hors ligne est volontairement limité :

- consulter les chevaux déjà téléchargés ;
- consulter l'historique déjà téléchargé ;
- créer une nouvelle séance localement sans réseau ;
- synchroniser automatiquement lorsque l'application est active et le réseau disponible ;
- afficher l'état de chaque séance et les erreurs corrigeables.

La modification/suppression offline de séances déjà synchronisées est exclue du MVP.

## Règle fondamentale : écriture locale atomique

Lors de la création d'une séance :

1. générer un UUID client avant la sauvegarde ;
2. valider localement les champs évidents (champs requis, formats, durée non négative, etc.) sans prétendre remplacer la validation serveur ;
3. dans **une seule transaction SQLite**, insérer la séance et son opération outbox ;
4. confirmer le succès à l'interface seulement après la validation de la transaction ;
5. afficher la séance immédiatement avec un état « En attente de synchronisation ».

Il ne doit jamais exister de séance locale en attente sans entrée outbox correspondante, ni d'entrée outbox pointant vers une séance absente.

## Composants

Créer un service de synchronisation dédié, par exemple :

```text
src/sync/
  sync-manager.ts
  sync-queue.ts
  sync-push.ts
  sync-pull.ts
  sync-status.ts
```

Adapter les noms au style du projet. Garder les composants UI indépendants du protocole réseau.

## Envoi (push)

- Traiter les opérations dans un ordre déterministe ; commencer par les créations de séances.
- Conserver le même UUID client et le même payload logique lors d'un retry.
- Éviter deux synchronisations concurrentes de la même outbox.
- Marquer une entrée `in_progress` de façon récupérable ; au redémarrage, remettre en attente les entrées restées bloquées après un crash.
- Envoyer le token d'accès sans le logger.
- Sur succès serveur, enregistrer `server_id`, `synced_at` et l'état synchronisé dans une transaction locale, puis terminer l'outbox.
- Le serveur doit garantir l'idempotence ; le client ne doit jamais générer un nouvel UUID lors d'un retry.

### Traitement des erreurs

| Erreur | Comportement |
|---|---|
| absence réseau / timeout | conserver l'opération, retry plus tard avec backoff |
| HTTP 5xx | retry avec backoff et jitter raisonnables |
| HTTP 401 | tenter un renouvellement une fois ; sinon demander reconnexion sans perdre l'outbox |
| HTTP 400 | marquer en erreur corrigeable, présenter les erreurs de champs |
| HTTP 403/404 | ne pas retry en boucle ; signaler l'accès refusé/ressource indisponible |
| HTTP 409 | traiter comme conflit/idempotency mismatch ; ne pas écraser automatiquement |

Le nombre d'essais et le dernier message d'erreur sont conservés. Les messages affichés à l'utilisateur doivent être compréhensibles, sans détails techniques sensibles.

## Réception (pull)

Pour le premier MVP, utiliser une synchronisation snapshot paginée si le volume de données est modeste :

1. récupérer toutes les pages autorisées de chevaux ;
2. récupérer les pages de séances ;
3. appliquer les pages dans SQLite en préservant les séances locales en attente ;
4. n'effectuer le nettoyage des lignes absentes que lorsque toutes les pages d'un snapshot ont été récupérées avec succès ;
5. enregistrer la date du dernier snapshot complet.

Si le volume est déjà trop important, proposer un protocole incrémental robuste (curseur serveur opaque ou couple timestamp + identifiant, gestion des modifications et tombstones). Ne pas ajouter un simple `updated_after` sans traiter les égalités de timestamp, suppressions et reprises après pagination.

Ne jamais effacer le cache local après une réponse réseau partielle ou un échec de pagination.

## Déclencheurs

- au démarrage/après authentification ;
- au retour de l'application au premier plan ;
- lorsque la connectivité semble revenir ;
- action manuelle « Synchroniser » si utile.

La détection réseau (par ex. Expo Network) n'est qu'un signal : chaque requête peut encore échouer. Le code doit toujours tolérer timeout et perte de réseau.

Ne pas dépendre des tâches de fond pour garantir la synchronisation. Une éventuelle tâche Expo BackgroundTask est opportuniste et hors garantie de délai.

## Authentification et changement de compte

- Conserver les opérations en attente associées à leur compte d'origine.
- Après déconnexion, ne jamais les envoyer sous le compte suivant.
- À la reconnexion, ne reprendre que les opérations du même compte.
- Si un compte a des opérations en attente, informer l'utilisateur avant une déconnexion destructive ou une suppression de données.
- Si le refresh token expire, conserver les données locales et demander une reconnexion.

## Conflits et limites du MVP

- Les séances créées hors ligne sont des créations ; le serveur décide si elles sont valides.
- Une séance déjà synchronisée n'est pas modifiable/supprimable hors ligne dans cette version.
- Un UUID réutilisé avec un payload différent est un conflit, pas une mise à jour silencieuse.
- Les chevaux sont des données de référence consultables localement ; les modifications de chevaux restent gérées en ligne/web dans le MVP.

## Tests indispensables

- création locale sans réseau ;
- écriture séance + outbox atomique ;
- fermeture/redémarrage et reprise ;
- upload réussi ;
- réponse perdue après création serveur puis retry (aucun doublon) ;
- réseau indisponible pendant l'envoi ;
- erreur 400 et correction/reprise ;
- erreur 401 et refresh ;
- erreur 409 ;
- crash avec entrée `in_progress` ;
- deux déclenchements simultanés ne doublonnent pas ;
- pagination interrompue ne détruit pas le cache ;
- compte A déconnecté puis compte B connecté : aucune opération de A n'est envoyée sous B.

## Critères d'acceptation

- [ ] Création d'une séance hors ligne immédiatement visible.
- [ ] La séance et l'outbox sont enregistrées atomiquement.
- [ ] Retry réseau sans doublon serveur.
- [ ] Statuts et erreurs sont visibles et compréhensibles.
- [ ] Le cache est préservé en cas de téléchargement interrompu.
- [ ] Les données sont isolées par utilisateur.
- [ ] Les tests de reprise, de panne et d'idempotence passent.
