#!/usr/bin/env bash
set -e  # arrêter le script si une commande échoue

# Variables — adapte-les
PROJECT_NAME="la_mulerie_training"
REPO_URL="git@github.com:TobisAuBonLaitDeBrebis/la-mulerie-training.git"
APP_DIR="/var/www/$PROJECT_NAME"
VENV_DIR="$APP_DIR/venv"
DJANGO_SETTINGS_MODULE="la_mulerie_training.settings.production"
# (ou settings selon ton config)
PYTHON_BIN="$VENV_DIR/bin/python"
PIP_BIN="$VENV_DIR/bin/pip"
GUNICORN_BIN="$VENV_DIR/bin/gunicorn"
# Nom du socket / port pour Gunicorn
GUNICORN_SOCK="/run/gunicorn/$PROJECT_NAME.sock"
GUNICORN_WORKERS=3
# Nom de ton service systemd (si tu en utilises un)
SERVICE_NAME="gunicorn_$PROJECT_NAME"

echo "=== Déploiement de $PROJECT_NAME ==="

# 1. Si le dossier de l’application n’existe pas, le cloner
if [ ! -d "$APP_DIR" ]; then
  echo "-- Clonage du dépôt"
  git clone $REPO_URL $APP_DIR
fi

cd $APP_DIR

# 2. Récupérer les modifications
echo "-- Récupérer les dernières modifications"
git fetch origin
git reset --hard origin/main      # ou master selon branche principale
git clean -fd                     # supprime les fichiers non suivis

# 3. (Re)création / activation de l’environnement virtuel
if [ ! -d "$VENV_DIR" ]; then
  echo "-- Création de l’environnement virtuel"
  python3 -m venv $VENV_DIR
fi

echo "-- Activation de l’environnement"
# shellcheck disable=SC1090
source $VENV_DIR/bin/activate

# 4. Installation des dépendances
echo "-- Installation des dépendances"
$PIP_BIN install --upgrade pip
$PIP_BIN install -r requirements.txt

# 5. Collecte des fichiers statiques
echo "-- Collecte des fichiers statiques"
$PYTHON_BIN manage.py collectstatic --noinput --settings=$DJANGO_SETTINGS_MODULE

# 6. Appliquer les migrations
echo "-- Appliquer les migrations"
$PYTHON_BIN manage.py migrate --noinput --settings=$DJANGO_SETTINGS_MODULE

# 7. Redémarrer le service (gunicorn ou autre)
echo "-- Redémarrage du service $SERVICE_NAME"
systemctl daemon-reload || true
systemctl restart $SERVICE_NAME

echo "=== Déploiement terminé ==="
