# About

Files mounted into the container and used by Websoft9.

## Where to put your code

- Put your Laravel project in `/var/www/html` (the `laravel_app` volume). It must contain `artisan`.
- Restart the app from the Websoft9 console after changing code.

## Default behavior

- If `/var/www/html` is empty, a default Laravel application is created (SQLite, no database service).
- `DATABASE_URL` is optional. Uncomment it in `.env` to connect an external database (`mysql://` or `postgres://`); the runtime maps it to Laravel's `DB_CONNECTION`/`DB_URL`.

## Customize the deploy steps

Add hooks under `/var/www/html/.w9/entrypoint.d/`:

- same filename replaces the package hook
- new filename is inserted in filename order
- override the start step with `/var/www/html/.w9/start.sh`

Available variables: `APP_DIR`, `W9_HTTP_PORT`, `W9_VERSION`.
