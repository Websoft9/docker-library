#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/src/app}"
PACKAGE_MANAGER="${PACKAGE_MANAGER:-npm}"

cd "${APP_DIR}"

if [ -d node_modules ]; then
  echo "[nextjs-runtime] node_modules already present; skipping install"
  exit 0
fi

echo "[nextjs-runtime] Installing dependencies with ${PACKAGE_MANAGER}..."
case "${PACKAGE_MANAGER}" in
  pnpm)
    corepack enable
    pnpm install --frozen-lockfile || pnpm install
    ;;
  yarn)
    corepack enable
    yarn install --immutable || yarn install
    ;;
  npm)
    if [ -f package-lock.json ]; then
      npm ci
    else
      npm install
    fi
    ;;
  *)
    echo "Unsupported package manager: ${PACKAGE_MANAGER}" >&2
    exit 1
    ;;
esac
