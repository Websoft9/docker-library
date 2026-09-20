#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/src/app}"
PACKAGE_MANAGER="${PACKAGE_MANAGER:-npm}"
PORT="${W9_HTTP_PORT:-3000}"

cd "${APP_DIR}"

case "${PACKAGE_MANAGER}" in
  pnpm)
    corepack enable
    exec pnpm start -- --hostname 0.0.0.0 --port "${PORT}"
    ;;
  yarn)
    corepack enable
    exec yarn start --hostname 0.0.0.0 --port "${PORT}"
    ;;
  npm)
    exec npm run start -- --hostname 0.0.0.0 --port "${PORT}"
    ;;
  *)
    echo "Unsupported package manager: ${PACKAGE_MANAGER}" >&2
    exit 1
    ;;
esac
