# Laravel

This package runs a production-style Laravel stack: FrankenPHP (Caddy) on PHP 8.3, MySQL 8.4, and a named volume that holds the application code.

## Put your own code in

- The application lives in the `laravel_app` named volume, mounted at `/var/www/html`.
- On first start, if no application is present, a default Laravel 13 application is created so you see the welcome page.
- To use your own code, upload it into the `laravel_app` volume (for example through the Websoft9 console file manager or a helper container), then restart the app.
- After uploading, the one-shot `permissions` service fixes file ownership for `www-data`, and `composer install` plus `php artisan migrate` run automatically on start.

## Database

- A MySQL 8.4 service is bundled. Connection settings are exposed in `.env` (`DB_*`).
- Container environment variables override the application's own `.env`, so editing `DB_*` in the Websoft9 console is enough.

## Notes

- The webroot is `/var/www/html/public`; never serve the project root.
- `APP_KEY` is generated in the application's `.env` on first scaffold and is not managed by the container environment.
