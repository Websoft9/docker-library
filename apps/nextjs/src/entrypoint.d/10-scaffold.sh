#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/src/app}"
NEXTJS_VERSION="${W9_VERSION:-latest}"
NEXTJS_CREATE_FLAGS="${NEXTJS_CREATE_FLAGS:---yes --use-npm}"

if [ -f "${APP_DIR}/package.json" ]; then
  echo "[nextjs-runtime] Next.js application detected; skipping scaffold"
  exit 0
fi

tmp_root="$(mktemp -d)"
tmp_dir="${tmp_root}/app"
mkdir -p "${tmp_dir}"

echo "[nextjs-runtime] No Next.js application found; creating a default Next.js application..."
npx "create-next-app@${NEXTJS_VERSION}" "${tmp_dir}" ${NEXTJS_CREATE_FLAGS}
cp -a "${tmp_dir}/." "${APP_DIR}/"
rm -rf "${tmp_root}"
echo "[nextjs-runtime] Default Next.js application created."
