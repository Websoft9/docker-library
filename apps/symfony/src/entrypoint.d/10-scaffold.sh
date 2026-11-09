#!/bin/sh
set -e

APP_DIR="${APP_DIR:-/var/www/html}"

if [ -f "${APP_DIR}/bin/console" ]; then
  echo "[symfony-runtime] Symfony application detected; skipping scaffold"
else
  echo "[symfony-runtime] No Symfony application found; creating a starter project..."
  TMP_ROOT="$(mktemp -d)"
  composer create-project symfony/skeleton "${TMP_ROOT}/app" \
    --no-interaction --prefer-dist

  case "${W9_VERSION:-}" in
    ""|latest|stable) FRAMEWORK_REQUIREMENT="" ;;
    *) FRAMEWORK_REQUIREMENT="symfony/framework-bundle:${W9_VERSION}" ;;
  esac

  if [ -n "${FRAMEWORK_REQUIREMENT}" ]; then
    composer require "${FRAMEWORK_REQUIREMENT}" \
      --working-dir="${TMP_ROOT}/app" --no-interaction --no-progress
  fi

  cp -a "${TMP_ROOT}/app/." "${APP_DIR}/"
  rm -rf "${TMP_ROOT}"

  mkdir -p "${APP_DIR}/src/Controller"
  cat > "${APP_DIR}/src/Controller/HomeController.php" <<'PHP'
<?php

namespace App\Controller;

use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;

final class HomeController
{
    #[Route('/', name: 'app_home')]
    public function __invoke(): Response
    {
        return new Response('Symfony application is ready.');
    }
}
PHP

  if ! grep -q '^APP_SECRET=[^[:space:]]' "${APP_DIR}/.env.local" 2>/dev/null; then
    printf 'APP_SECRET=%s\n' "$(php -r 'echo bin2hex(random_bytes(32));')" >> "${APP_DIR}/.env.local"
  fi

  echo "[symfony-runtime] Starter project created."
fi
