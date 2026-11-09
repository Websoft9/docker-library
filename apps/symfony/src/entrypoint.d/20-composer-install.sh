#!/bin/sh
set -e

APP_DIR="${APP_DIR:-/var/www/html}"

if [ -f "${APP_DIR}/composer.json" ] && [ ! -f "${APP_DIR}/vendor/autoload.php" ]; then
  echo "[symfony-runtime] Installing Composer dependencies..."
  cd "${APP_DIR}"
  composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader
fi
