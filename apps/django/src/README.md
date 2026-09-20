# About

Files mounted into the container and used by Websoft9.

## Where to put your code

- Put your Django project in `/app` (the `django_app` volume). It must contain `manage.py`.
- Restart the app from the Websoft9 console after changing code.

## Default behavior

- If `/app` is empty, a default Django project is created with a native `settings.py` (SQLite).
- The runtime wrapper `project/settings_runtime.py` applies environment overrides without editing `settings.py`.
- `DATABASE_URL` is optional. Uncomment it in `.env` to use PostgreSQL or MySQL instead of SQLite.

## Customize the deploy steps

Add hooks under `/app/.w9/entrypoint.d/`:

- same filename replaces the package hook
- new filename is inserted in filename order
- override the start step with `/app/.w9/start.sh`

Hooks run as UID 1000 with `APP_DIR` as the working directory. Available variables: `APP_DIR`, `W9_HTTP_PORT`, `W9_VERSION`, `DJANGO_SETTINGS_MODULE`.
