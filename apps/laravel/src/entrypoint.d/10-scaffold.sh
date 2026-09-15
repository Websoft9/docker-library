#!/bin/sh
set -e

APP_DIR=/var/www/html

case "${W9_VERSION:-}" in
  ""|latest|main|stable) FRAMEWORK_REQUIREMENT="" ;;
  *) FRAMEWORK_REQUIREMENT="laravel/framework:${W9_VERSION}" ;;
esac

if [ -f "$APP_DIR/artisan" ]; then
  echo "Laravel application detected at $APP_DIR"
else
  echo "No Laravel application found; creating a default Laravel application..."
  TMP_DIR="$(mktemp -d)"
  composer create-project laravel/laravel "$TMP_DIR" \
    --no-interaction --prefer-dist --no-scripts
  if [ -n "$FRAMEWORK_REQUIREMENT" ]; then
    echo "Pinning framework to ${FRAMEWORK_REQUIREMENT}"
    composer require "$FRAMEWORK_REQUIREMENT" \
      --working-dir="$TMP_DIR" --no-interaction --no-scripts --no-progress
  fi
  cp -a "$TMP_DIR/." "$APP_DIR/"
  rm -rf "$TMP_DIR"
  echo "Default Laravel application created."
fi

cd "$APP_DIR"

if [ ! -f .env ] && [ -f .env.example ]; then
  echo "Creating .env from .env.example"
  cp .env.example .env
fi

if [ -f .env ] && ! grep -q '^APP_KEY=base64:' .env; then
  echo "Generating application key"
  php artisan key:generate --force
fi
