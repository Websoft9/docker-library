#!/bin/sh
set -e

APP_DIR=/app
VENV="$APP_DIR/.venv"
PROJECT="${DJANGO_PROJECT:-project}"

cd "$APP_DIR"

case "${W9_VERSION:-}" in
  ""|latest|main|stable) DJANGO_REQUIREMENT="Django" ;;
  *) DJANGO_REQUIREMENT="Django==${W9_VERSION}" ;;
esac
DEPS_MARKER="${DJANGO_REQUIREMENT}|deps-2"

if [ ! -d "$VENV" ] || [ "$(cat "$VENV/.deps-marker" 2>/dev/null)" != "$DEPS_MARKER" ]; then
  echo "Preparing virtual environment (${DJANGO_REQUIREMENT})..."
  [ -d "$VENV" ] || python -m venv "$VENV"
  . "$VENV/bin/activate"
  pip install --quiet --upgrade pip
  pip install --quiet "$DJANGO_REQUIREMENT" gunicorn "psycopg[binary]" whitenoise django-mcp-server "mcp<2"
  echo "$DEPS_MARKER" > "$VENV/.deps-marker"
else
  . "$VENV/bin/activate"
fi

if [ -f requirements.txt ]; then
  echo "Installing requirements.txt..."
  pip install --quiet -r requirements.txt
fi

if [ ! -f manage.py ]; then
  echo "No Django project found; creating a default project..."
  django-admin startproject "$PROJECT" .
  cat >> "$PROJECT/settings.py" <<'PYEOF'

# --- Websoft9 runtime overrides (environment based) ---
import os

SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "*").split(",") if host]
CSRF_TRUSTED_ORIGINS = [origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "django"),
        "USER": os.environ.get("DB_USER", "django"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

# MCP endpoint (no authentication by default; secure it before exposing publicly)
INSTALLED_APPS.append("mcp_server")
DJANGO_MCP_GLOBAL_SERVER_CONFIG = {"name": "django"}

_mcp_auth = os.environ.get("DJANGO_MCP_AUTHENTICATION_CLASSES", "").strip()
if _mcp_auth:
    DJANGO_MCP_AUTHENTICATION_CLASSES = [c.strip() for c in _mcp_auth.split(",") if c.strip()]
    for _app in ("rest_framework", "rest_framework.authtoken"):
        if _app not in INSTALLED_APPS:
            INSTALLED_APPS.append(_app)
PYEOF
  cat > "$PROJECT/urls.py" <<'PYEOF'
import os

from django.contrib import admin
from django.http import HttpResponse
from django.urls import include, path

_admin_path = os.environ.get("W9_ADMIN_PATH", "/admin").strip("/") or "admin"

urlpatterns = [
    path(f"{_admin_path}/", admin.site.urls),
    path("", include("mcp_server.urls")),
    path("", lambda request: HttpResponse("Django is running.")),
]
PYEOF
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput >/dev/null 2>&1 || true

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
  if python manage.py shell -c "from django.contrib.auth import get_user_model; import os, sys; sys.exit(0 if get_user_model().objects.filter(username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists() else 1)"; then
    echo "Superuser ${DJANGO_SUPERUSER_USERNAME} already exists."
  else
    echo "Creating superuser ${DJANGO_SUPERUSER_USERNAME}..."
    python manage.py createsuperuser --noinput || true
  fi
fi

exec gunicorn "${PROJECT}.wsgi:application" \
  --bind "0.0.0.0:8000" \
  --workers "${GUNICORN_WORKERS:-3}"
