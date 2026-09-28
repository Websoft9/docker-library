#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/local/tomcat}"
cd "${APP_DIR}"

# Restore the bundled default webapps (ROOT, docs, examples) that the official
# image keeps in webapps.dist. Idempotent: safe to run on every start.
mkdir -p webapps

if [ -d webapps.dist ]; then
  echo "[tomcat-runtime] restoring default webapps into ${APP_DIR}/webapps"
  cp -a webapps.dist/. webapps/
fi
