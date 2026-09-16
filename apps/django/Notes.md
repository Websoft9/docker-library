# Django

This package runs a production-style Django stack: Gunicorn (WSGI) on Python 3.13, PostgreSQL 17, and a named volume that holds the application code.

## Put your own code in

- The application lives in the `django_app` named volume, mounted at `/app`.
- On first start, if no project is present, a default Django project is created, and the admin login is available at `/admin/`.
- Upload your own code into the `django_app` volume, then restart the app.
- The one-shot `permissions` service fixes ownership for UID 1000, and dependencies are installed into `/app/.venv` on start.

## Database

- PostgreSQL 17 is bundled. Connection settings are exposed in `.env` (`DB_*`).
- The generated `settings.py` override reads `DB_*`; if you bring your own settings, read the same variables so console changes take effect.

## Notes

- The web server is Gunicorn; `manage.py runserver` is not used.
- `SECRET_KEY` defaults to `W9_POWER_PASSWORD`; set a dedicated value in production.
- `DEBUG=false` and `ALLOWED_HOSTS=*` by default; restrict `ALLOWED_HOSTS` in production.

## Agent integration (MCP)

- `django-mcp-server` is installed in the scaffolded project and exposes an MCP endpoint at `/mcp` (streamable HTTP) on the same port as the app, served by the same Gunicorn process. No extra container or port is required.
- No authentication is enabled by default. To enable it, set `DJANGO_MCP_AUTHENTICATION_CLASSES` in `.env` to a comma-separated list of DRF authentication class paths (for example `rest_framework.authentication.TokenAuthentication`); the scaffold then adds `rest_framework` and `rest_framework.authtoken` to `INSTALLED_APPS` automatically.
- Publish your own tools by adding `ModelQueryToolset` / `MCPToolset` classes in your app's `mcp.py`.

