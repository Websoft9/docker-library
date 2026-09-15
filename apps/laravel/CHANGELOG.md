# CHANGELOG

## 2026-09-15

- Reworked the package from a self-built `php:8.3-apache` image into the maintained `serversideup/php:8.3-frankenphp-debian` image (FrankenPHP application server), removing the custom `Dockerfile` and the old PHP build scripts.
- Added a bundled MySQL 8.4 service and exposed the Laravel database connection (`DB_*`) and application settings (`APP_*`) through `.env`.
- Added a `laravel_app` named volume for the application code, plus a one-shot `permissions` service that fixes ownership for `www-data`.
- Added `src/entrypoint.d/` startup scripts that scaffold a default Laravel 13 application on first start, create `.env`, generate `APP_KEY`, and run `composer install` when `vendor/` is missing.
- Declared `variables.json.access` for the web console (container port 8080).
- Decoupled the user-facing version from the image tag: `W9_VERSION` now carries the Laravel framework version (for appstore selection), the FrankenPHP image tag is hardcoded in `docker-compose.yml`, and the scaffold pins `laravel/framework` to `${W9_VERSION}`.
