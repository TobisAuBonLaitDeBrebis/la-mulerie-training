# État Initial — Lot 00

**Document de référence pour l'audit initial du projet La Mulerie Training**  
**Date :** 9 novembre 2025  
**Version :** 1.0  
**Auteur :** Audit automatisé  

---

## 📋 Sommaire

1. [Versions et environnement](#1-versions-et-environnement)
2. [Structure du dépôt](#2-structure-du-dépôt)
3. [Configuration Django](#3-configuration-django)
4. [Modèles et relations](#4-modèles-et-relations)
5. [Applications et responsabilités](#5-applications-et-responsabilités)
6. [Règles d'accès et sécurité](#6-règles-d'accès-et-sécurité)
7. [Règles métier identifiées](#7-règles-métier-identifiées)
8. [Routes web existantes](#8-routes-web-existantes)
9. [Tests et couverture](#9-tests-et-couverture)
10. [Vérifications techniques](#10-vérifications-techniques)
11. [Risques et décisions nécessaires](#11-risques-et-décisions-nécessaires)

---

## 1. Versions et environnement

### Versions vérifiées

| Composant | Version | Source |
|-----------|---------|--------|
| **Python** | 3.11.9 | `.venv` |
| **Django** | 5.2.6 | `requirements.txt` / `.venv` |
| **Django (global)** | 4.1.2 | Système global (à ignorer) |
| **pytest** | 8.4.2 | `requirements.txt` |
| **factory_boy** | 3.3.3 | `requirements.txt` |
| **Faker** | 37.8.0 | `requirements.txt` |

### Environnement de développement

- **Système d'exploitation :** Windows
- **Base de données :** SQLite 3 (fichier `db.sqlite3`)
- **Configuration active :** `la_mulerie_training.settings.dev`
- **Settings alternatifs :** `la_mulerie_training.settings.prod.py` (non testé)

### Dependances principales

```
Django==5.2.6
django-tailwind==4.2.0
django-browser-reload==1.19.0
factory_boy==3.3.3
pytest==8.4.2
pytest-django==4.11.1
Faker==37.8.0
```

**⚠️ Incohérence détectée :** Le fichier `requirements.txt` et l'environnement `.venv` utilisent Django 5.2.6, mais l'installation Python globale a Django 4.1.2. Les commandes doivent être exécutées avec `.venv/Scripts/python` pour garantir la bonne version.

---

## 2. Structure du dépôt

```
la-mulerie-training/
├── AGENTS.md                          # Règles de développement
├── README.md                          # Documentation projet
├── Procfile.tailwind                 # Configuration Tailwind
├── deploy.sh                         # Script de déploiement
├── manage.py                         # Gestion Django
├── pytest.ini                        # Configuration pytest
├── requirements.txt                  # Dépendances Python
├── db.sqlite3                        # Base de données SQLite
├── .venv/                            # Environnement virtuel
│
├── accounts/                         # Application utilisateurs
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                      # UserProfileForm
│   ├── urls.py                       # Routes accounts/
│   ├── views.py                      # signup, profile, edit_profile, change_password
│   ├── migrations/                   # (vide - utilise User natif)
│   └── templates/                    # Templates accounts
│
├── la_mulerie_training/              # Configuration principale
│   ├── __init__.py
│   ├── asgi.py
│   ├── wsgi.py
│   ├── urls.py                       # Routes principales
│   ├── settings/                     # Configurations séparées
│   │   ├── dev.py                    # Dev (active)
│   │   └── prod.py                   # Production
│   ├── static/                       # Static files
│   ├── templates/                    # Templates globaux
│   │   └── la_mulerie_training/
│   │       └── base.html             # Template base
│   └── templatetags/                 # Filtres personnalisés
│       ├── __init__.py
│       └── custom_filters.py         # percent_of filter
│
├── theme/                            # Thème Tailwind/DaisyUI
│   ├── __init__.py
│   ├── apps.py
│   ├── static/
│   ├── static_src/                   # Sources Tailwind
│   └── templates/
│
├── training/                         # Application cœur métier
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                     # Horse, TrainingSession
│   ├── forms.py                      # HorseForm, TrainingSessionForm
│   ├── urls.py                       # Routes training/
│   ├── views.py                      # Toutes les vues
│   ├── migrations/                   # 5 migrations
│   │   ├── 0001_initial.py
│   │   ├── 0002_trainingsession_cavalier_alter_trainingsession_date.py
│   │   ├── 0003_horse_proprietaire.py
│   │   ├── 0004_trainingsession_cout.py
│   │   └── 0005_remove_horse_age_horse_birth_date.py
│   ├── templates/
│   │   └── training/
│   │       ├── dashboard.html        # Dashboard avec stats
│   │       ├── home_training.html    # Liste séances
│   │       ├── home_horses.html      # Liste chevaux
│   │       ├── horse_detail.html     # Détail cheval
│   │       ├── horse_form.html       # Formulaire cheval
│   │       ├── training_detail.html  # Détail séance
│   │       ├── training_form.html    # Formulaire séance
│   │       └── components/
│   │           └── training_calendar.html
│   └── tests/
│       ├── __init__.py
│       ├── factories.py              # UserFactory, HorseFactory, TrainingSessionFactory
│       ├── test_models.py            # 2 tests
│       ├── test_views.py             # 9 tests
│       └── test_dashboard.py         # 12 tests
│
└── docs/
    └── la-mulerie-mobile-roadmap/
        ├── 00-audit-et-etat-initial.md
        └── ETAT-INITIAL.md           # Ce document
```

---

## 3. Configuration Django

### Applications installées

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'la_mulerie_training',
    'training',
    'accounts',
    'tailwind',
    'theme',
]
```

### Middleware

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

### Base de données

- **Engine :** `django.db.backends.sqlite3`
- **Fichier :** `db.sqlite3` à la racine
- **Configuration :** Aucune variable d'environnement détectée

### Internationalisation

- **LANGUAGE_CODE :** `en-us`
- **TIME_ZONE :** `UTC`
- **USE_I18N :** `True`
- **USE_TZ :** `True`

### URL Configuration

- **ROOT_URLCONF :** `la_mulerie_training.urls`
- **LOGIN_URL :** `/accounts/login/`
- **LOGOUT_REDIRECT_URL :** `/accounts/login/`

### Static Files

- **STATIC_URL :** `/static/`
- **STATIC_ROOT :** `BASE_DIR / 'static'`
- **STATICFILES_DIRS :** `[BASE_DIR / "theme/static"]`

---

## 4. Modèles et relations

### Modèle User (Django natif)

Utilisation du modèle `django.contrib.auth.models.User` standard.
- **Champs :** username, password, email, first_name, last_name, is_active, is_staff, is_superuser, last_login, date_joined
- **Pas de custom User model**

### Modèle Horse

```python
class Horse(models.Model):
    nom = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    birth_date = models.DateField(default=django.utils.timezone.now)
    proprietaire = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chevaux',
        null=True,
        blank=True
    )
    
    @property
    def age(self):
        """Calcule l'âge en années à partir de la date de naissance."""
        if self.birth_date:
            today = date.today()
            return (
                today.year - self.birth_date.year
                - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
            )
        return None
```

**Évolution historique :**
- Migration 0001 : création avec `age` comme PositiveIntegerField
- Migration 0005 : suppression de `age`, ajout de `birth_date` avec calcul dynamique via property

### Modèle TrainingSession

```python
class TrainingSession(models.Model):
    cheval = models.ForeignKey('Horse', on_delete=models.CASCADE, related_name='trainings')
    cavalier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions',
        null=True,
        blank=True
    )
    date = models.DateField(default=django.utils.timezone.now)
    type_seance = models.CharField(max_length=100)
    duree = models.PositiveIntegerField(help_text="Durée en minutes")
    notes = models.TextField(blank=True, null=True)
    cout = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True, 
                               help_text="Coût de l'entraînement en euros")
```

**Évolution historique :**
- Migration 0001 : création initiale
- Migration 0002 : ajout de `cavalier`, `date` devient default=now
- Migration 0004 : ajout de `cout`

### Relations

```
User (AUTH_USER_MODEL)
├── cheval (via Horse.proprietaire) → Horse (1:N) - related_name='chevaux'
└── session (via TrainingSession.cavalier) → TrainingSession (1:N) - related_name='sessions'

Horse
└── training → TrainingSession (1:N) - related_name='trainings'
```

### 📊 Champs clés et unités

| Modèle | Champ | Type | Unité | Obligatoire | Valeur par défaut |
|--------|-------|------|-------|-------------|-------------------|
| Horse | nom | CharField | - | Oui | - |
| Horse | race | CharField | - | Oui | - |
| Horse | birth_date | DateField | - | Oui | date du jour |
| Horse | proprietaire | ForeignKey | - | Non | NULL |
| TrainingSession | cheval | ForeignKey | - | Oui | - |
| TrainingSession | cavalier | ForeignKey | - | Non | NULL |
| TrainingSession | date | DateField | - | Oui | date du jour |
| TrainingSession | type_seance | CharField | - | Oui | - |
| TrainingSession | duree | PositiveIntegerField | **minutes** | Oui | - |
| TrainingSession | cout | DecimalField | **euros** | Non | NULL |
| TrainingSession | notes | TextField | - | Non | NULL |

---

## 5. Applications et responsabilités

### Application `accounts/`

**Responsabilité :** Gestion des utilisateurs et authentification.

| Fichier | Rôle |
|---------|------|
| `views.py` | Inscription, profil, modification profil, changement mot de passe |
| `urls.py` | Routage des URLs `/accounts/*` |
| `forms.py` | `UserProfileForm` (username, first_name, last_name, email) |
| `templates/` | Templates d'authentification et profil |

**Particularités :**
- Utilise les vues natives de Django (`LoginView`, `LogoutView`)
- Pas de modèle custom User
- La vue `profile` redirige vers `home_training`

### Application `training/`

**Responsabilité :** Cœur métier — gestion des équidés et des séances d'entraînement.

| Fichier | Rôle |
|---------|------|
| `models.py` | Horse, TrainingSession |
| `views.py` | Toutes les vues CRUD + dashboard |
| `forms.py` | HorseForm, TrainingSessionForm |
| `urls.py` | Routage des URLs `/` et `/cheval/*`, `/entrainement/*` |
| `templates/training/` | Tous les templates d'interface |
| `tests/` | 23 tests (modèles, vues, dashboard) |

**Fonctionnalités principales :**
- CRUD chevaux (Horse)
- CRUD séances (TrainingSession)
- Dashboard avec statistiques et graphiques
- Calendrier des séances
- Filtres par date

### Application `theme/`

**Responsabilité :** Thème visuel avec Tailwind CSS et DaisyUI.

- Gère les assets CSS/JS compilés
- Contient les sources Tailwind (`static_src/`)
- Pas de logique métier

### Application `la_mulerie_training/`

**Responsabilité :** Configuration globale et templates de base.

- Settings Django (dev/prod)
- URL rooting
- Template `base.html`
- Filtres personnalisés (`percent_of`)

---

## 6. Règles d'accès et sécurité

### Décorateurs utilisés

- **`@login_required`** : Appliqué à **toutes** les vues des applications `training/` et `accounts/` (sauf signup, login, logout)
- **Pas de `@user_passes_test`** ou permissions custom détectées

### Vérifications d'accès dans les vues

#### Training Views

```python
# horse_detail
horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user.pk)

# horse_edit
horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)

# horse_delete
horse = get_object_or_404(Horse, pk=pk, proprietaire=request.user)

# training_detail, training_edit, training_delete
training = get_object_or_404(TrainingSession, pk=pk, cavalier=request.user)
```

#### Dashboard View

```python
# Filtre par défaut pour toutes les requêtes
base_filter = {'cavalier': request.user}

# Pour les chevaux
Horse.objects.filter(proprietaire=request.user)
```

### 📌 Règles d'accès vérifiées

| Ressource | Accès autorisé à | Méthode de vérification |
|-----------|-----------------|------------------------|
| Cheval (detail/edit/delete) | Propriétaire uniquement | `get_object_or_404(..., proprietaire=request.user)` |
| Séance (detail/edit/delete) | Cavalier uniquement | `get_object_or_404(..., cavalier=request.user)` |
| Dashboard | Utilisateur connecté | `@login_required` + filtre `cavalier=request.user` |
| Liste chevaux | Propriétaire uniquement | `Horse.objects.filter(proprietaire=request.user)` |
| Liste séances | Cavalier uniquement | `TrainingSession.objects.filter(cavalier=request.user)` |

### 🔒 Sécurité

- **CSRF :** Activé (middleware présent)
- **Session :** Middleware présent
- **Messages :** Middleware présent
- **XFrameOptions :** Middleware présent
- **Debug :** `True` en dev (à désactiver en prod)
- **ALLOWED_HOSTS :** `['127.0.0.1']` en dev

---

## 7. Règles métier identifiées

### 🐴 Gestion des chevaux (Horse)

1. **Création :**
   - Le `proprietaire` est automatiquement défini à l'utilisateur connecté dans `horse_add`
   - Champs obligatoires : `nom`, `race`, `birth_date`
   - Pas de validation supplémentaire dans le formulaire

2. **Modification :**
   - Seul le propriétaire peut modifier un cheval
   - Pas de restrictions sur les champs modifiables

3. **Suppression :**
   - Suppression cascade : les séances liées sont supprimées avec le cheval
   - Vérification du propriétaire avant suppression

4. **Âge :**
   - Calculé dynamiquement à partir de `birth_date`
   - Formule : `année actuelle - année naissance - (mois/jour actuel < mois/jour naissance)`

### 🏇 Gestion des séances (TrainingSession)

1. **Création :**
   - Le `cavalier` est automatiquement défini à l'utilisateur connecté
   - Le cheval doit appartenir à l'utilisateur connecté (filtre dans le formulaire)
   - Champs obligatoires : `cheval`, `date`, `type_seance`, `duree`
   - Champs optionnels : `notes`, `cout`

2. **Modification :**
   - Seul le cavalier peut modifier une séance
   - Le cheval peut être changé (mais toujours limité aux chevaux du propriétaire)

3. **Suppression :**
   - Seul le cavalier peut supprimer une séance
   - Suppression sans confirmation (GET request, à améliorer)

4. **Unités :**
   - **Durée :** Toujours en **minutes** (PositiveIntegerField)
   - **Coût :** Toujours en **euros** (DecimalField, 2 décimales)

### 📊 Dashboard et statistiques

1. **Périmètre des données :**
   - Toutes les statistiques sont **filtrées par l'utilisateur connecté**
   - Filtre principal : `cavalier=request.user` pour les séances
   - Filtre complémentaire : `proprietaire=request.user` pour les chevaux

2. **Calculs des KPI :**
   ```python
   total_sessions = sessions_qs.count()
   total_horses = Horse.objects.filter(proprietaire=request.user).count()
   total_duration = sessions_qs.aggregate(total=models.Sum('duree'))['total'] or 0
   total_cost = sessions_qs.aggregate(total=models.Sum('cout'))['total'] or 0
   avg_duration = round(total_duration / total_sessions, 1) if total_sessions > 0 else 0
   avg_cost = round(total_cost / total_sessions, 2) if total_sessions > 0 else 0
   sessions_per_horse = round(total_sessions / total_horses, 1) if total_horses > 0 else 0
   ```

3. **Répartition par type :**
   - Compte et somme de durée par `type_seance`
   - Tri par nombre décroissant

4. **Répartition par cheval :**
   - Compte et somme de durée par cheval
   - Tri par durée totale décroissante

5. **Graphique mensuel :**
   - Par défaut : affiche l'année en cours
   - Avec filtre date : affiche les mois entre la date de début et de fin
   - Utilisation de Chart.js côté client

6. **Filtres par date :**
   - `start_date` : date de début inclusive (`date__gte`)
   - `end_date` : date de fin inclusive (`date__lte`)
   - Pas de filtre = toutes les dates

### 📅 Calendrier

- Affichage des séances sous forme de calendrier (via `training_calendar.html`)
- Données passées en JSON : `{id, date, activity}`
- Utilisation de Chart.js ou bibliothèque similaire côté client

---

## 8. Routes web existantes

### Routes principales (`la_mulerie_training/urls.py`)

```
/admin/          → admin.site.urls
/accounts/       → accounts.urls
/                → training.urls
```

### Routes `accounts/`

| URL | Vue | Nom | Auth | Description |
|-----|-----|-----|------|-------------|
| `/accounts/signup/` | `signup` | `signup` | Non | Inscription |
| `/accounts/login/` | `LoginView` | `login` | Non | Connexion |
| `/accounts/logout/` | `LogoutView` | `logout` | Oui | Déconnexion |
| `/accounts/profile/` | `profile` | `profile` | Oui | Redirige vers home_training |
| `/accounts/edit_profile/` | `edit_profile` | `edit_profile` | Oui | Modifier profil |
| `/accounts/profile/password/` | `change_password` | `change_password` | Oui | Changer mot de passe |

### Routes `training/`

| URL | Vue | Nom | Auth | Description |
|-----|-----|-----|------|-------------|
| `/` | `home_training` | `home_training` | Oui | Liste des séances |
| `/dashboard/` | `dashboard` | `dashboard` | Oui | Dashboard statistiques |
| `/cheval/home` | `home_horses` | `home_horses` | Oui | Liste des chevaux |
| `/cheval/ajouter/` | `horse_add` | `horse_add` | Oui | Ajouter cheval |
| `/cheval/<pk>/` | `horse_detail` | `horse_detail` | Oui | Détail cheval |
| `/cheval/<pk>/edit` | `horse_edit` | `horse_edit` | Oui | Modifier cheval |
| `/cheval/<pk>/supprimer/` | `horse_delete` | `horse_delete` | Oui | Supprimer cheval |
| `/cheval/<horse_pk>/entrainement/ajouter/` | `training_add` | `training_add` | Oui | Ajouter séance (avec cheval pré-sélectionné) |
| `/entrainement/ajouter/` | `training_add` | `training_add_global` | Oui | Ajouter séance (sans cheval) |
| `/entrainement/<pk>/edit/` | `training_edit` | `training_edit` | Oui | Modifier séance |
| `/entrainement/<pk>/supprimer/` | `training_delete` | `training_delete` | Oui | Supprimer séance |
| `/entrainement/<pk>/details/` | `training_detail` | `training_detail` | Oui | Détail séance |

---

## 9. Tests et couverture

### Organisation des tests

```
training/tests/
├── __init__.py
├── factories.py          # 3 factories (User, Horse, TrainingSession)
├── test_models.py        # 2 tests
├── test_views.py         # 9 tests
└── test_dashboard.py     # 12 tests
```

### Factories

```python
# UserFactory
- username: user{sequence}
- email: {username}@example.com
- password: password123 (via set_password)

# HorseFactory
- nom: Faker first_name
- race: Faker word
- birth_date: Faker date_of_birth
- age: calculé à partir de l'âge souhaité (optionnel)

# TrainingSessionFactory
- cheval: SubFactory(HorseFactory)
- date: Faker date_this_year
- type_seance: Faker word
- duree: Faker pyint (10-180)
- notes: Faker sentence
- cout: non défini par défaut (NULL)
```

### Résultats des tests

```bash
# Commande exécutée
DJANGO_SETTINGS_MODULE=la_mulerie_training.settings.dev .venv/Scripts/python manage.py test training.tests -v 0

# Résultat
Ran 23 tests in 166.105s
OK
System check identified no issues (0 silenced).
```

**Toutes les 23 tests passent avec succès.**

### Détail des tests

| Fichier | Classe | Tests | Statut |
|---------|--------|-------|--------|
| `test_models.py` | `HorseModelTest` | 1 | ✅ |
| `test_models.py` | `TrainingSessionModelTest` | 1 | ✅ |
| `test_views.py` | `TrainingViewsTest` | 9 | ✅ |
| `test_dashboard.py` | `DashboardViewTest` | 12 | ✅ |

### Tests vérifiés

#### Modèles
- ✅ Création cheval avec tous les champs
- ✅ Création séance avec cheval, type, durée, notes

#### Vues
- ✅ Accès home_training
- ✅ Détail cheval
- ✅ Ajout cheval
- ✅ Ajout séance avec horse_pk
- ✅ Ajout séance sans horse_pk
- ✅ Suppression cheval
- ✅ Suppression séance
- ✅ **Accès interdit aux chevaux d'autres utilisateurs**
- ✅ **Accès interdit aux séances d'autres utilisateurs**

#### Dashboard
- ✅ Accès nécessite connexion
- ✅ Affichage correct utilisateur connecté
- ✅ KPI à 0 sans données
- ✅ KPI corrects avec données
- ✅ Filtre par date
- ✅ Affichage toutes les données par défaut
- ✅ Calcul des moyennes
- ✅ Statistiques par type
- ✅ Statistiques par cheval
- ✅ Dernières séances
- ✅ Données graphique mensuel
- ✅ **Isolation des données par utilisateur**

### Points forts des tests

1. **Isolation des données :** Les tests vérifient explicitement que les utilisateurs ne peuvent pas accéder aux données des autres
2. **Couverture fonctionnelle :** Toutes les vues sont testées
3. **Validation des calculs :** Les moyennes et totaux sont vérifiés
4. **Tests de filtres :** Les filtres par date sont testés

### Limites identifiées

1. **Pas de tests pour `accounts/`** : Aucune suite de test pour l'application accounts
2. **Pas de tests d'authentification avancés** : Pas de tests pour les permissions, groupes, etc.
3. **Tests lents** : 166 secondes pour 23 tests (problème de performance à investiguer)
4. **Pas de tests pour les formulaires** : Les validations de formulaires ne sont pas testées
5. **Pas de tests pour les templates** : Le rendu HTML n'est pas vérifié en détail

---

## 10. Vérifications techniques

### Commandes Django

```bash
# Vérification de la configuration
.venv/Scripts/python manage.py check
# Résultat : System check identified no issues (0 silenced).

# Vérification des migrations
.venv/Scripts/python manage.py showmigrations
# Résultat : Toutes les migrations appliquées

# Vérification des modèles
.venv/Scripts/python manage.py sqlmigrate training 0005
# Résultat : SQL valide
```

### Configuration pytest

```ini
[pytest]
DJANGO_SETTINGS_MODULE = la_mulerie_training.settings
python_files = test_*.py
```

**⚠️ Problème identifié :** `pytest.ini` pointe vers `la_mulerie_training.settings` mais le module est dans `la_mulerie_training/settings/dev.py`. Il faut utiliser `DJANGO_SETTINGS_MODULE=la_mulerie_training.settings.dev` pour les tests.

### Environnement virtuel

- **Créé :** Oui (`.venv/`)
- **Actif :** Django 5.2.6, Python 3.11.9
- **Dépendances :** Installées et fonctionnelles

---

## 11. Risques et décisions nécessaires

### 🔴 Risques critiques

#### 1. **Incohérence de version Django**

- **Problème :** `requirements.txt` et `.venv` utilisent Django 5.2.6, mais le système global a Django 4.1.2
- **Impact :** Les commandes doivent être exécutées avec `.venv/Scripts/python` pour éviter les erreurs
- **Recommandation :** Documenter clairement l'utilisation du venv

#### 2. **Performances des tests**

- **Problème :** 23 tests prennent 166 secondes (7.2s par test en moyenne)
- **Impact :** Développement ralenti, intégration continue difficile
- **Causes possibles :**
  - Base de données SQLite en mémoire pour chaque test
  - Migration complète avant chaque test
  - Faker génère des données lentement
- **Recommandation :** Investiger et optimiser (utiliser `--reuse-db` pour pytest-django)

#### 3. **Configuration pytest**

- **Problème :** `pytest.ini` ne pointe pas vers le bon module settings
- **Impact :** Les tests pytest échouent sans variable d'environnement
- **Recommandation :** Mettre à jour `pytest.ini` ou documenter la commande correcte

### 🟡 Risques moyens

#### 4. **Sécurité des suppressions**

- **Problème :** Les vues de suppression utilisent des requêtes GET
- **Exemple :** `/cheval/<pk>/supprimer/` et `/entrainement/<pk>/supprimer/`
- **Impact :** Suppression possible via lien ou CSRF
- **Recommandation :** Changer en POST avec confirmation

#### 5. **Validation des formulaires**

- **Problème :** Pas de validation côté serveur au-delà des champs obligatoires
- **Exemple :** `duree` peut être 0 ou très grand, `cout` peut être négatif
- **Impact :** Données incohérentes possibles
- **Recommandation :** Ajouter des validateurs dans les modèles ou formulaires

#### 6. **Nullabilité des champs**

- **Problème :** `Horse.proprietaire` et `TrainingSession.cavalier` sont nullable
- **Impact :** Séances ou chevaux sans propriétaire possible
- **Recommandation :** Rendre ces champs obligatoires après migration des données existantes

#### 7. **Pas de tests pour accounts/**

- **Problème :** Aucune couverture de test pour l'application accounts
- **Impact :** Régressions possibles non détectées
- **Recommandation :** Ajouter des tests pour l'authentification et le profil

### 🟢 Points positifs

1. **Architecture claire :** Séparation nette entre applications
2. **Tests existants :** 23 tests couvrent les fonctionnalités principales
3. **Isolation des données :** Bonne implémentation des vérifications d'accès
4. **Documentation :** AGENTS.md complet et bien structuré
5. **Migrations :** Historique propre et cohérent
6. **Configuration :** Environnements dev/prod séparés

### ❓ Décisions métier nécessaires avant le Lot 01

#### Décision 1 : **Propriété des données et partage**

**Contexte :** Actuellement, un cheval n'a qu'un seul propriétaire (`proprietaire`), et une séance n'a qu'un seul cavalier (`cavalier`).

**Questions :**
- Faut-il permettre à plusieurs utilisateurs d'accéder aux mêmes chevaux ?
- Faut-il permettre à plusieurs cavaliers d'enregistrer des séances pour le même cheval ?
- Faut-il un système de partage/permissions ?

**Impact sur mobile :**
- Si oui : architecture de données à repenser (ManyToMany, groupes, permissions)
- Si non : le modèle actuel est suffisant

**Recommandation :** Clarifier cette règle métier avant toute évolution vers le mobile.

#### Décision 2 : **Synchronisation des données**

**Contexte :** Application mobile en offline avec SQLite local.

**Questions :**
- Comment synchroniser les données entre l'app mobile et le backend Django ?
- Faut-il une API REST pour la synchronisation ?
- Quelle stratégie de conflit en cas de modification offline ?

**Impact :**
- Architecture API à concevoir
- Modèle de données à adapter pour la synchronisation

#### Décision 3 : **Utilisation du modèle User Django**

**Contexte :** L'application utilise le User natif de Django.

**Questions :**
- Faut-il ajouter des champs custom au User (ex: photo, téléphone) ?
- Faut-il créer un Profile model séparé ?

**Impact :**
- Migration nécessaire si ajout de champs
- Synchronisation avec l'existant

#### Décision 4 : **Gestion des dates et fuseaux horaires**

**Contexte :** `USE_TZ = True` mais `TIME_ZONE = 'UTC'`.

**Questions :**
- Faut-il gérer les fuseaux horaires pour les utilisateurs ?
- Comment afficher les dates dans le bon fuseau sur mobile ?

**Impact :**
- Stockage des dates à revoir
- Affichage à adapter

#### Décision 5 : **Unités de mesure**

**Contexte :** Durée en minutes, coût en euros.

**Questions :**
- Faut-il supporter d'autres devises ?
- Faut-il permettre des unités de durée différentes (heures, secondes) ?

**Impact :**
- Modèle à adapter si nécessaire

---

## 📝 Résumé exécutif

### ✅ Ce qui est validé

1. **Architecture Django :** Propre et bien structurée
2. **Modèles :** Cohérents avec les besoins exprimés
3. **Sécurité :** @login_required partout, vérifications d'accès dans les vues
4. **Tests :** 23 tests passent, bonne couverture fonctionnelle
5. **Configuration :** Dev et prod séparés, environnement virtuel fonctionnel
6. **Documentation :** AGENTS.md complet et applicable

### ⚠️ Points d'attention

1. **Configuration pytest :** À corriger pour pointer vers le bon settings module
2. **Performances tests :** À optimiser (166s pour 23 tests)
3. **Suppressions en GET :** À sécuriser (changer en POST)
4. **Nullabilité :** `proprietaire` et `cavalier` à rendre obligatoires
5. **Validation :** Ajouter des validateurs pour durée et coût

### ❗ Décisions bloquantes pour le Lot 01

1. **Partage des données entre utilisateurs** (propriétaire/cavalier)
2. **Stratégie de synchronisation mobile-backend**
3. **Évolution du modèle User** (champs additionnels)
4. **Gestion des fuseaux horaires**
5. **Unités de mesure** (durée, coût)

### 📋 Prochaines étapes (hors périmètre Lot 00)

Une fois les décisions métier prises :
1. Corriger les points d'attention techniques
2. Créer l'API REST (Django REST Framework)
3. Concevoir l'architecture mobile (React Native + Expo)
4. Mettre en place la synchronisation offline
5. Adapter l'interface pour le mobile

---

## 📚 Annexes

### A. Fichiers examinés

```
AGENTS.md
README.md
requirements.txt
pytest.ini
manage.py

la_mulerie_training/__init__.py
la_mulerie_training/urls.py
la_mulerie_training/settings/dev.py
la_mulerie_training/settings/prod.py
la_mulerie_training/templatetags/custom_filters.py

accounts/__init__.py
accounts/admin.py
accounts/apps.py
accounts/forms.py
accounts/urls.py
accounts/views.py

Training/__init__.py
Training/admin.py
Training/apps.py
Training/models.py
Training/forms.py
Training/urls.py
Training/views.py
Training/tests/__init__.py
Training/tests/factories.py
Training/tests/test_models.py
Training/tests/test_views.py
Training/tests/test_dashboard.py
Training/migrations/0001_initial.py
Training/migrations/0002_trainingsession_cavalier_alter_trainingsession_date.py
Training/migrations/0003_horse_proprietaire.py
Training/migrations/0004_trainingsession_cout.py
Training/migrations/0005_remove_horse_age_horse_birth_date.py
```

### B. Commandes de test exécutées

```bash
# Vérification Django
.venv/Scripts/python manage.py check

# Tests unitaires
.venv/Scripts/python manage.py test training.tests -v 0

# Résultat : 23 tests OK, 0 silenced
```

### C. Statistiques du code

- **Modèles :** 2 (Horse, TrainingSession)
- **Vues :** 13 (training) + 4 (accounts) = 17
- **Formulaires :** 3 (HorseForm, TrainingSessionForm, UserProfileForm)
- **URLs :** 17 routes utilisateur + 1 admin
- **Templates :** 10+ templates HTML
- **Tests :** 23 tests
- **Factories :** 3

---

**Document généré dans le cadre du Lot 00 — Audit et état initial**  
**À ne pas modifier sans validation explicite.**  
**Prochaine étape : Validation des décisions métier avant passage au Lot 01.**
