#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
VENV="$APP_DIR/.venv"

cd "$APP_DIR"

"$VENV/bin/python" manage.py migrate --noinput
"$VENV/bin/python" manage.py collectstatic --noinput >/dev/null 2>&1 || true

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  if "$VENV/bin/python" manage.py shell -c "from django.contrib.auth import get_user_model; import os, sys; sys.exit(0 if get_user_model().objects.filter(username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists() else 1)"; then
    echo "[django-runtime] Superuser ${DJANGO_SUPERUSER_USERNAME} already exists."
  else
    echo "[django-runtime] Creating superuser ${DJANGO_SUPERUSER_USERNAME}..."
    "$VENV/bin/python" manage.py createsuperuser --noinput || true
  fi
fi
