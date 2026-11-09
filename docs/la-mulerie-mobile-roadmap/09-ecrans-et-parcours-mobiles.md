# Lot 09 — Écrans et parcours mobiles

**Dépendances :** lots 05, 07 et 08.  
**But :** construire l'interface iOS/Android native au-dessus des repositories locaux et de la synchronisation.

## Principes UX

- Interface utilisable à une main et rapidement dans un environnement d'écurie.
- Les écrans lisent les données via les repositories locaux, pas directement depuis `fetch`/HTTP.
- Les actions sont enregistrées localement avant confirmation à l'utilisateur.
- L'état réseau et l'état de synchronisation sont distincts.
- Les composants sont natifs React Native ; ne pas encapsuler les templates Django dans une WebView.
- Réutiliser logos, images, textes et identité graphique existants lorsque les assets le permettent, mais ne pas essayer de réutiliser le HTML Django comme UI native.

## Parcours MVP

### A. Authentification

- écran de connexion ;
- conservation sécurisée du refresh token ;
- restauration de session si possible ;
- expiration/renouvellement ;
- déconnexion avec avertissement si des séances sont encore en attente.

Ne pas afficher les écrans privés tant que l'identité de compte n'est pas établie. Les données déjà mises en cache restent cloisonnées.

### B. Liste et détail des équidés

- liste locale, disponible hors ligne ;
- recherche/filtre uniquement si utile au volume ;
- fiche équidé avec les données mises en cache ;
- état « données mises à jour le … » ou indication de cache si la fraîcheur est importante.

### C. Historique des séances

- liste locale des séances ;
- filtrage par équidé et période si les API et repositories le permettent ;
- distinction visuelle entre « En attente », « Synchronisée » et « À corriger » ;
- une séance en attente reste consultable et ne disparaît pas en cas d'erreur.

### D. Création rapide d'une séance

- choisir un équidé déjà disponible localement ;
- choisir un type selon les valeurs réellement définies dans le projet ;
- saisir les champs présents dans le modèle ;
- validation locale basique ;
- sauvegarde SQLite atomique avec outbox ;
- confirmation immédiate, même sans réseau.

Ne pas inventer de nouveaux champs métier ou de nouvelles unités sans décision produit.

### E. Tableau de bord

- afficher les statistiques fournies par l'API lorsque le réseau est disponible ;
- définir les indicateurs pouvant être recalculés localement à partir du cache ;
- si calcul local : réutiliser exactement les règles métier documentées et tester la cohérence avec Django ;
- indiquer clairement quand les statistiques sont issues des seules données téléchargées et peuvent être incomplètes.

## État global de synchronisation

Prévoir un composant réutilisable avec au minimum :

- hors ligne ;
- synchronisation en cours ;
- synchronisé ;
- éléments en attente ;
- erreur nécessitant une action utilisateur.

Ne pas afficher « Synchronisé » si des opérations échouées ou en attente existent pour le compte actif.

## Accessibilité et ergonomie

- tailles de zones tactiles suffisantes ;
- libellés accessibles ;
- contrastes lisibles en extérieur ;
- formulaires avec clavier adapté ;
- confirmation pour les actions irréversibles ;
- éviter les saisies longues et répétitives.

## Tests requis

- navigation des parcours principaux ;
- liste des chevaux avec et sans réseau ;
- création d'une séance offline ;
- reprise après fermeture de l'application ;
- statuts de synchronisation ;
- erreurs de validation ;
- session expirée ;
- changement de compte avec opérations en attente ;
- tests sur petits et grands formats d'écran si disponibles.

## Hors périmètre

- fonctionnalités non présentes dans le métier web ;
- édition/suppression offline de séances synchronisées ;
- photos, vidéos, GPS ou capteurs non demandés ;
- publication stores.

## Critères d'acceptation

- [ ] Les parcours MVP sont natifs et fonctionnent avec les données locales.
- [ ] La création de séance ne dépend pas du réseau.
- [ ] Les états offline/synchronisation sont explicites.
- [ ] Les données locales ne sont pas confondues entre comptes.
- [ ] L'interface reste utilisable dans les conditions d'usage visées.
