#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/app}"
VENV="$APP_DIR/.venv"
PROJECT="${DJANGO_PROJECT:-project}"

cd "$APP_DIR"

if [ ! -f manage.py ]; then
  echo "[django-runtime] No Django project found; creating a default project..."
  "$VENV/bin/django-admin" startproject "$PROJECT" .
fi

if [ ! -f "$PROJECT/settings.py" ]; then
  echo "[django-runtime] $PROJECT/settings.py not found; skipping runtime wrapper"
  exit 0
fi

# Runtime wrapper: keeps the native settings.py/urls.py untouched and applies
# environment overrides on top of them.
cat > "$PROJECT/settings_runtime.py" <<PYEOF
from .settings import *
import os

SECRET_KEY = os.environ.get("SECRET_KEY", SECRET_KEY)
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"
ALLOWED_HOSTS = [host for host in os.environ.get("ALLOWED_HOSTS", "*").split(",") if host]
CSRF_TRUSTED_ORIGINS = [origin for origin in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if origin]

STATIC_ROOT = BASE_DIR / "staticfiles"
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

ROOT_URLCONF = "${PROJECT}.urls_runtime"

INSTALLED_APPS.append("mcp_server")
DJANGO_MCP_GLOBAL_SERVER_CONFIG = {"name": "django"}

_mcp_auth = os.environ.get("DJANGO_MCP_AUTHENTICATION_CLASSES", "").strip()
if _mcp_auth:
    DJANGO_MCP_AUTHENTICATION_CLASSES = [c.strip() for c in _mcp_auth.split(",") if c.strip()]
    for _app in ("rest_framework", "rest_framework.authtoken"):
        if _app not in INSTALLED_APPS:
            INSTALLED_APPS.append(_app)

# Optional external database. When DATABASE_URL is set it overrides the native
# DATABASES entry; otherwise the project keeps its native settings (SQLite).
_database_url = os.environ.get("DATABASE_URL", "").strip()
if _database_url:
    from urllib.parse import urlparse

    _parsed = urlparse(_database_url)
    _engines = {
        "postgres": "django.db.backends.postgresql",
        "postgresql": "django.db.backends.postgresql",
        "mysql": "django.db.backends.mysql",
        "mariadb": "django.db.backends.mysql",
    }
    _engine = _engines.get(_parsed.scheme)
    if _engine:
        DATABASES["default"] = {
            "ENGINE": _engine,
            "NAME": (_parsed.path or "").lstrip("/") or DATABASES["default"].get("NAME", ""),
            "USER": _parsed.username or "",
            "PASSWORD": _parsed.password or "",
            "HOST": _parsed.hostname or "",
            "PORT": str(_parsed.port or ""),
        }
PYEOF

cat > "$PROJECT/urls_runtime.py" <<PYEOF
from django.http import HttpResponse
from django.urls import include, path

from .urls import urlpatterns as _native_urlpatterns

urlpatterns = _native_urlpatterns + [
    path("", include("mcp_server.urls")),
    path("", lambda request: HttpResponse("Django is running.")),
]
PYEOF
