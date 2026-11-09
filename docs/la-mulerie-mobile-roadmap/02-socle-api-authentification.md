# Lot 02 — Socle API et authentification mobile

**Dépendance :** lot 01 terminé.  
**But :** ajouter une API versionnée sans modifier le mode de fonctionnement du site web.

## Objectif

Installer Django REST Framework et poser une base d'API cohérente, testée et sécurisée. Le site web continue d'utiliser l'authentification Django existante ; le mobile dispose d'un mécanisme adapté aux clients natifs.

## Analyse préalable

- Vérifier les versions installées de Python et Django et leur compatibilité avec la version DRF envisagée.
- Examiner `settings`, `urls`, `AUTH_USER_MODEL`, middleware, gestion des environnements et tests.
- Vérifier si une API ou une dépendance équivalente existe déjà.
- Examiner la politique CORS uniquement si un client navigateur séparé en a besoin ; une application native n'est pas soumise au même modèle CORS qu'un navigateur.

## Implémentation

### A. Dépendances et configuration

- Ajouter DRF avec une version compatible, en respectant le gestionnaire de dépendances du dépôt.
- Ajouter un mécanisme JWT pour le client mobile (évaluer SimpleJWT et sa compatibilité actuelle).
- Ajouter le générateur OpenAPI dans le lot 05, sauf si le projet en a besoin dès le socle.
- Ne pas désactiver CSRF pour les vues web.
- Prévoir des paramètres DRF explicites : authentification, permissions par défaut, pagination, format d'erreur et throttling si pertinent.

### B. Préfixe et santé de l'API

Créer le préfixe `/api/v1/` sans modifier les routes web existantes.

Ajouter au minimum un endpoint authentifié `/api/v1/me/` retournant uniquement les champs de profil nécessaires au mobile (identifiant stable, nom d'affichage ou équivalent déjà disponible). Ne pas exposer le modèle utilisateur complet.

Ajouter éventuellement un endpoint de santé non sensible si le déploiement en a réellement besoin ; ne pas exposer de diagnostics détaillés ou de secrets.

### C. Authentification

- Prévoir connexion, renouvellement et déconnexion/révocation si le mécanisme choisi le permet.
- Vérifier les options de rotation et de blacklist/révocation des refresh tokens avec la version installée.
- Définir précisément les durées de vie selon l'environnement et documenter les compromis.
- Les secrets doivent provenir de variables d'environnement ou de la configuration sécurisée du déploiement.
- Le client mobile stockera le refresh token dans SecureStore ; l'access token ne doit pas être journalisé.
- Ne jamais renvoyer des tokens dans des URLs.
- Les endpoints privés utilisent une permission d'authentification explicite. Un utilisateur non authentifié reçoit un code 401 cohérent.

Ne pas implémenter une authentification maison si une solution maintenue compatible suffit.

### D. Gestion des erreurs

Définir une réponse d'erreur DRF stable et documentée, sans divulguer les traces Python ou les détails internes en production. Les erreurs de validation doivent rester exploitables par l'application mobile.

## Tests requis

- `/api/v1/me/` refuse un utilisateur anonyme.
- Un utilisateur authentifié reçoit uniquement les champs prévus.
- Connexion avec identifiants valides/invalides.
- Accès refusé sans token, token invalide ou expiré.
- Renouvellement valide/invalide et révocation si configurée.
- Le comportement d'authentification des pages web existantes n'est pas modifié.
- Les paramètres de production ne divulguent pas les détails d'erreur.

## Hors périmètre

- endpoints chevaux et séances ;
- refactorisation complète des vues ;
- application Expo ;
- synchronisation hors ligne.

## Critères d'acceptation

- [ ] DRF est installé et configuré de manière minimale.
- [ ] `/api/v1/me/` fonctionne avec l'authentification choisie.
- [ ] Le site web conserve ses sessions et sa protection CSRF.
- [ ] Secrets et tokens ne sont pas exposés dans le dépôt ou les logs.
- [ ] Tests API et tests web passent.
- [ ] Dépendances et variables d'environnement sont documentées.
