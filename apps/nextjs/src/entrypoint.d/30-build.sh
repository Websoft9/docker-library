#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/src/app}"
PACKAGE_MANAGER="${PACKAGE_MANAGER:-npm}"

cd "${APP_DIR}"

if [ -f .next/BUILD_ID ]; then
  echo "[nextjs-runtime] Existing build found; skipping build"
  exit 0
fi

echo "[nextjs-runtime] Building Next.js application..."
case "${PACKAGE_MANAGER}" in
  pnpm)
    corepack enable
    pnpm run build
    ;;
  yarn)
    corepack enable
    yarn build
    ;;
  npm)
    npm run build
    ;;
  *)
    echo "Unsupported package manager: ${PACKAGE_MANAGER}" >&2
    exit 1
    ;;
esac
