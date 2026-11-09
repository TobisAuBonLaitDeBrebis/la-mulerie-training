# Architecture cible — La Mulerie Training

## 1. Vue d'ensemble

```text
                         ┌──────────────────────────┐
                         │       Site web actuel    │
                         │ Django Templates + HTMX  │
                         └────────────┬─────────────┘
                                      │ vues web
┌──────────────────────────┐          │          ┌──────────────────────────┐
│ Application iOS/Android  │          │          │      API REST JSON       │
│ React Native + Expo      ├──────────┴──────────┤ Django REST Framework    │
│                          │                     │                          │
│ UI → repositories SQLite │                     │ serializers / permissions│
│        ↕                 │                     │                          │
│ SQLite + outbox          │  HTTPS + JSON       │ mêmes modèles et règles  │
│        ↕                 ├────────────────────►│ métier Django             │
│ sync manager             │                     │                          │
└──────────────────────────┘                     └────────────┬─────────────┘
                                                             │ ORM
                                                  ┌──────────▼─────────────┐
                                                  │ Base distante existante│
                                                  └────────────────────────┘
```

Il s'agit d'un **monolithe Django avec deux interfaces**, pas de deux backends. L'API ne doit pas dupliquer la logique métier déjà présente dans les vues web.

## 2. Responsabilités

### Django

- source de référence des données synchronisées ;
- authentification et autorisation ;
- validation métier côté serveur ;
- API versionnée sous `/api/v1/` ;
- calculs statistiques communs au web et au mobile ;
- administration et interface web existantes.

### Application mobile

- affichage natif iOS/Android ;
- persistance locale des données nécessaires ;
- saisie locale immédiate ;
- enregistrement atomique d'une mutation et de sa tâche outbox ;
- reprise/synchronisation ;
- présentation claire des états hors ligne et des erreurs.

### SQLite

SQLite est une copie de travail locale, pas une base partagée entre appareils. Ne pas considérer un identifiant local comme un identifiant serveur.

## 3. Règles de données

- Chaque séance créée sur mobile reçoit un UUID client stable avant toute requête réseau.
- L'UUID client reste identique lors de toutes les tentatives d'envoi.
- Le serveur associe cet UUID à l'utilisateur authentifié et garantit l'unicité de la création.
- Le serveur dérive l'utilisateur depuis le jeton authentifié ; il ne fait jamais confiance à un `user_id`, `cavalier` ou propriétaire fourni librement dans le corps de la requête.
- Les modèles et relations réels du dépôt déterminent la règle d'accès. Ne pas supposer qu'un propriétaire et un cavalier ont les mêmes droits.
- Les données locales sont cloisonnées par compte (`account_id`/identifiant serveur stable). Les données d'un compte ne sont jamais transmises sous l'identité d'un autre.
- Les dates, heures, fuseaux et unités doivent conserver exactement la sémantique des champs Django existants.

## 4. Premier modèle de synchronisation

Le MVP porte d'abord sur la création hors ligne de séances :

1. Le mobile crée une séance dans SQLite avec un UUID client.
2. Dans la même transaction SQLite, il crée une entrée dans `sync_outbox`.
3. L'interface affiche immédiatement la séance avec l'état « En attente ».
4. Le sync manager transmet les opérations en attente lorsque l'application est active et que le réseau est disponible.
5. Django valide les permissions et les données puis crée ou retrouve la séance associée à l'UUID client.
6. Le mobile reçoit l'identifiant serveur et passe la séance à l'état « Synchronisée ».
7. Si la réponse se perd, le même UUID est renvoyé ; le serveur ne crée pas de doublon.

Les échecs de validation ne doivent pas être traités comme des erreurs réseau : ils deviennent visibles et corrigibles par l'utilisateur. Les erreurs réseau et serveur temporaires sont réessayées avec temporisation.

## 5. Stratégie de téléchargement initiale

Pour le premier MVP, préférer une synchronisation snapshot paginée, simple et vérifiable, si les volumes restent modestes :

- télécharger toutes les pages de chevaux accessibles ;
- télécharger les pages de séances accessibles ;
- appliquer chaque page dans une transaction locale ;
- ne jamais supprimer les séances locales en attente ;
- ne marquer un snapshot comme complet qu'une fois toutes les pages reçues ;
- ne supprimer/expirer les données distantes locales absentes qu'après un snapshot complet, jamais après une synchronisation interrompue.

Si les volumes sont déjà importants, proposer une synchronisation incrémentale avec curseur et gestion explicite des suppressions (`deleted_at`/tombstones). Ne pas introduire un curseur fragile basé uniquement sur une date sans départager les éléments ayant le même timestamp.

## 6. Stockage et sécurité

- SQLite : données métier locales et outbox.
- SecureStore : jeton de renouvellement (et autres secrets strictement nécessaires).
- Jeton d'accès : mémoire autant que possible ; ne pas le loguer.
- HTTPS obligatoire en production.
- Ne jamais placer les secrets dans les fichiers `.env` suivis par Git.
- La base SQLite n'est pas automatiquement chiffrée par le simple fait d'utiliser `expo-sqlite`. Si un besoin de chiffrement local est identifié, le traiter comme une décision de sécurité dédiée.
- À la déconnexion, préserver les opérations en attente dans l'espace local de leur compte ; prévenir l'utilisateur. Une autre session ne doit pas les envoyer.

## 7. Décisions volontairement reportées

- modification/suppression hors ligne de séances déjà synchronisées ;
- résolution automatique des conflits multi-appareils ;
- création hors ligne de chevaux ;
- synchronisation delta et tombstones si le snapshot paginé devient insuffisant ;
- tâches de synchronisation périodiques en arrière-plan ;
- pièces jointes/photos et synchronisation de fichiers.

Ces sujets ne doivent pas être ajoutés spontanément au premier MVP.
