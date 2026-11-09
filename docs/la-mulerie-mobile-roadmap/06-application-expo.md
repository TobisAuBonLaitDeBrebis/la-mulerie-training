# Lot 06 — Initialisation de l'application mobile Expo

**Dépendance :** lot 02 terminé (le développement des écrans métier attend les lots API).  
**But :** créer un socle React Native natif iOS/Android sans WebView.

## Objectif

Initialiser une application Expo avec TypeScript, navigation, configuration par environnement, qualité de code et un écran de démonstration. Ce lot ne doit pas encore implémenter toute la logique métier ni la synchronisation.

## Analyse préalable

- Examiner la structure et les outils présents à la racine (npm/pnpm/yarn, conventions, CI, gitignore).
- Ne pas remplacer le gestionnaire de paquets du dépôt s'il existe déjà une convention claire.
- Vérifier la compatibilité des versions actuelles d'Expo, React Native et Node.js dans la documentation officielle.
- Vérifier les exigences des machines de développement pour iOS et Android.

## Implémentation

### A. Projet

Créer `mobile/` à la racine du dépôt, sans déplacer les dossiers Django.

Utiliser :

- Expo ;
- React Native ;
- TypeScript strict autant que possible ;
- Expo Router pour la navigation si la version Expo retenue le recommande ;
- configuration distincte développement/staging/production sans secrets versionnés.

Utiliser les commandes d'installation Expo recommandées pour assurer la compatibilité des modules natifs. Ne pas choisir des versions arbitraires copiées depuis un ancien tutoriel.

### B. Structure initiale suggérée

```text
mobile/
  app/
    _layout.tsx
    index.tsx
  src/
    components/
    config/
    hooks/
    types/
    utils/
  assets/
  app.json (ou configuration Expo équivalente)
  package.json
  tsconfig.json
```

Adapter si Expo Router génère une structure différente. Éviter de créer des dossiers vides sans usage.

### C. Configuration réseau

- Définir une URL d'API par environnement.
- Ne pas utiliser `localhost` dans les builds installés sur un appareil physique ; documenter les adresses de développement nécessaires.
- Refuser une configuration production pointant vers une URL HTTP non sécurisée, sauf environnement local explicitement autorisé.
- Ne jamais committer de secret.

### D. Qualité et navigation

- Configurer TypeScript strict et le lint/test runner retenu après inspection.
- Créer les routes racines et un écran placeholder simple.
- Ajouter une gestion d'erreur non bloquante et une page de fallback si nécessaire.
- Préparer les identifiants d'application, icônes, splash screen et permissions uniquement lorsqu'ils sont connus et nécessaires.

## Tests et vérifications

- démarrage Expo en développement ;
- vérification TypeScript ;
- lint ;
- rendu sur au moins un simulateur/émulateur si disponible ;
- build de développement Android et iOS si l'environnement le permet ;
- expliquer honnêtement les plateformes non testées.

## Hors périmètre

- authentification complète ;
- écrans chevaux/séances ;
- SQLite ;
- synchronisation ;
- publication sur les stores.

## Critères d'acceptation

- [ ] `mobile/` fonctionne indépendamment du serveur Django.
- [ ] Le projet est TypeScript et utilise des composants React Native natifs.
- [ ] Les environnements et URLs API sont configurables.
- [ ] Aucun secret n'est versionné.
- [ ] Les instructions de lancement sont documentées.
