# Lot 10 — Recette, sécurité et préparation de publication

**Dépendances :** lots 00 à 09.  
**But :** valider le fonctionnement de bout en bout et préparer une distribution de test. Ce lot n'autorise pas une publication réelle sur les stores.

## 1. Recette fonctionnelle de bout en bout

Exécuter au minimum les scénarios suivants sur appareil ou simulateur et backend de test/staging :

1. Se connecter en ligne.
2. Télécharger les chevaux et séances autorisés.
3. Passer en mode avion.
4. Fermer complètement l'application et la relancer.
5. Vérifier que les données téléchargées restent visibles.
6. Créer une séance sans réseau.
7. Vérifier qu'elle apparaît immédiatement avec le statut en attente.
8. Fermer et relancer l'application ; vérifier sa persistance.
9. Restaurer le réseau.
10. Vérifier l'envoi, la confirmation serveur et le statut synchronisé.
11. Vérifier la présence d'une seule séance dans Django et dans le site web.
12. Simuler une réponse perdue après écriture serveur et vérifier qu'un retry ne crée pas de doublon.
13. Simuler une erreur de validation et vérifier qu'elle est visible et corrigeable.
14. Tester deux comptes successifs sur le même appareil et vérifier l'isolation des opérations en attente.

## 2. Sécurité

Vérifier :

- HTTPS en staging/production ;
- permissions API sur chaque ressource ;
- aucun accès inter-utilisateur ;
- absence de secrets dans Git, logs, analytics ou crash reports ;
- tokens dans SecureStore et jamais dans SQLite/AsyncStorage ;
- renouvellement et expiration des tokens ;
- limitation des endpoints sensibles si approprié ;
- validation serveur même si l'interface valide déjà ;
- aucune suppression via GET ;
- aucune opération outbox envoyée sous le mauvais compte.

## 3. Robustesse et données

- tester les migrations Django sur une copie de base non productive ;
- tester les migrations SQLite depuis une base vide et depuis chaque version de schéma réellement supportée ;
- interrompre volontairement la synchronisation au milieu d'une pagination ;
- tester les changements de connectivité répétés ;
- contrôler les fuseaux horaires, dates et unités ;
- vérifier qu'aucune opération locale n'est perdue en cas de fermeture forcée ;
- vérifier les erreurs de serveur et le comportement de retry.

## 4. Performance

Mesurer avant d'optimiser : temps d'ouverture, affichage liste, sauvegarde locale, taille du cache, durée de synchronisation. Ajouter pagination et index nécessaires. Ne pas remplacer Django par Rust pour des raisons hypothétiques de performance.

## 5. Distribution de test

Préparer, sans publier :

- configuration d'identifiants iOS et Android ;
- icône, splash screen, nom et version ;
- profils de build dev/staging/production ;
- variables d'environnement documentées ;
- build interne/test ;
- TestFlight et piste de test Google Play si les accès et comptes sont prêts.

Toute soumission réelle sur les stores, tout changement de compte développeur ou tout déploiement backend exige une demande explicite.

## 6. Documentation

Mettre à jour :

- README racine avec les commandes web et mobile ;
- configuration locale et environnements ;
- documentation API ;
- stratégie offline et limites MVP ;
- procédure de diagnostic des opérations en attente ;
- procédure de backup/restauration de la base distante (si nécessaire au déploiement).

## Critères d'acceptation

- [ ] Scénario complet offline → online exécuté.
- [ ] Aucun doublon après retry.
- [ ] Aucun mélange de données entre comptes.
- [ ] Tests backend et mobile exécutés et résultats consignés.
- [ ] Builds de test réalisés pour les plateformes disponibles.
- [ ] Limites et éléments non testés clairement signalés.
- [ ] Aucun déploiement ou publication effectué sans autorisation.
