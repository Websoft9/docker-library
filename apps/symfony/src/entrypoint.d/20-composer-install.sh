#!/bin/sh
set -e

APP_DIR="${APP_DIR:-/var/www/html}"

if [ -f "${APP_DIR}/composer.json" ] && [ ! -f "${APP_DIR}/vendor/autoload.php" ]; then
  echo "[symfony-runtime] Installing Composer dependencies..."
  cd "${APP_DIR}"
  composer install --no-dev --no-interaction --prefer-dist --optimize-autoloader
fi

if [ -f "${APP_DIR}/bin/console" ]; then
  ENV_NAME="${APP_ENV:-prod}"
  CACHE_DIR="${APP_DIR}/var/cache/${ENV_NAME}"

  # With APP_DEBUG=0 Symfony loads the compiled container as-is and never
  # revalidates it. A cache copied from the scaffold temp directory (absolute
  # /tmp paths) or a missing cache would then answer 404 for every route.
  if [ -d "${CACHE_DIR}" ] && grep -qs '"/tmp/' "${CACHE_DIR}"/*.meta; then
    echo "[symfony-runtime] Removing stale ${ENV_NAME} cache..."
    rm -rf "${CACHE_DIR}"
  fi

  if ! ls "${CACHE_DIR}"/*Container.php >/dev/null 2>&1; then
    echo "[symfony-runtime] Warming up the ${ENV_NAME} cache..."
    cd "${APP_DIR}"
    php bin/console cache:warmup --env="${ENV_NAME}" --no-interaction \
      || echo "[symfony-runtime] WARNING: cache warmup failed; the app will build it on first request"
  fi
fi
