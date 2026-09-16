# CHANGELOG

## 2026-09-15

- Created the Django package based on the maintained `python:3.13-slim` image, serving through Gunicorn (WSGI).
- Bundled PostgreSQL 17 and exposed the database connection (`DB_*`) plus Django settings (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`) through `.env`.
- Added a `django_app` named volume for the application code and a one-shot `permissions` service that fixes ownership for UID 1000.
- Added `src/entrypoint.sh` which scaffolds a default Django project on first start, appends an environment-based `settings.py` override, installs dependencies into a virtualenv, runs migrations, and starts Gunicorn.
- `W9_VERSION` carries the Django version for appstore selection; the Python image tag is hardcoded in `docker-compose.yml`.
- Declared `variables.json.access` for the web console and admin (container port 8000).
- Added a root liveness route so `/` returns a page, declared the admin login pair (`W9_LOGIN_USER`/`W9_LOGIN_PASSWORD`) and `W9_ADMIN_PATH=/admin`, and made the entrypoint create the Django superuser from those credentials on first start.
- The scaffolded `urls.py` now derives the admin route from `W9_ADMIN_PATH`, so the backend path is configurable through `.env`.
- Installed `django-mcp-server` in the scaffolded project and exposed an MCP endpoint at `/mcp` (streamable HTTP, no authentication by default). Pinned `mcp<2` because `django-mcp-server` imports `FastMCP` from `mcp.server`, which `mcp` 2.x removed.
- Added a `.env`-driven MCP authentication switch (`DJANGO_MCP_AUTHENTICATION_CLASSES`); when set, the scaffold registers the given DRF authentication classes and enables `rest_framework.authtoken`.
