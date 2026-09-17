#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
VENV="$APP_DIR/.venv"
PROJECT="${DJANGO_PROJECT:-project}"

cd "$APP_DIR"

exec "$VENV/bin/gunicorn" "${PROJECT}.wsgi:application" \
  --bind "0.0.0.0:8000" \
  --workers "${GUNICORN_WORKERS:-3}"
