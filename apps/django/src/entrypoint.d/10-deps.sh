#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
VENV="$APP_DIR/.venv"

case "${W9_VERSION:-}" in
  ""|latest|main|stable) DJANGO_REQUIREMENT="Django" ;;
  *) DJANGO_REQUIREMENT="Django==${W9_VERSION}" ;;
esac
DEPS_MARKER="${DJANGO_REQUIREMENT}|deps-3"

cd "$APP_DIR"

if [ ! -x "$VENV/bin/pip" ] || [ "$(cat "$VENV/.deps-marker" 2>/dev/null)" != "$DEPS_MARKER" ]; then
  echo "[django-runtime] Preparing virtual environment (${DJANGO_REQUIREMENT})..."
  [ -x "$VENV/bin/pip" ] || python -m venv "$VENV"
  "$VENV/bin/pip" install --quiet --upgrade pip
  "$VENV/bin/pip" install --quiet "$DJANGO_REQUIREMENT" gunicorn "psycopg[binary]" whitenoise django-mcp-server "mcp<2"
  echo "$DEPS_MARKER" > "$VENV/.deps-marker"
fi

if [ -f requirements.txt ]; then
  echo "[django-runtime] Installing requirements.txt..."
  "$VENV/bin/pip" install --quiet -r requirements.txt
fi
