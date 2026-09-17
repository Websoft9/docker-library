# Moodle

This package uses the upstream `elestio/moodle` image (no local Dockerfile). The image is based on
`moodlehq/moodle-php-apache` (PHP 8.4 + Apache) and installs Moodle automatically on first start.

## First start

- Moodle is installed non-interactively from the `MOODLE_*` variables in `.env`.
- `MOODLE_USERNAME` / `MOODLE_PASSWORD` become the initial site administrator.
- The install only runs when `/var/www/html/config.php` is missing, so these variables take effect
  on first start only.

## Persistence

- `moodle_html` → `/var/www/html` (Moodle source and `config.php`)
- `moodle_data` → `/var/moodledata` (uploaded files and caches)
- `mariadb_data` → `/var/lib/mysql`

Keep the `moodle_html` volume: if `config.php` is lost while the database still has data, the
image's installer drops the existing tables and reinstalls.

## PHP configuration

- PHP scan dir: `/usr/local/etc/php/conf.d/`
- The image ships Moodle defaults at `/usr/local/etc/php/conf.d/zz-moodle.ini`.
- `src/php.ini` is mounted to `/usr/local/etc/php/conf.d/zz-websoft9.ini` and overrides the defaults.
- You can also use `PHP_INI-<name>=<value>` environment variables, or mount any `*.ini` into
  `/docker-entrypoint.d/` (the entrypoint copies it into `conf.d`).

See `src/README.md` for details.

## Maintenance

- Moodle cron runs inside the container (the image starts it automatically).
- The bundled MariaDB uses utf8mb4 with `max_allowed_packet=512M`.
- Because the Moodle source lives in the `moodle_html` volume, an image version bump does not
  replace the source of an existing install. To move an existing install to a newer Moodle,
  refresh the source in that volume and run the Moodle upgrade from the admin UI or CLI.

## Websoft9 specifics

- `MOODLE_HOST` is `http://${W9_URL}`. Moodle validates `wwwroot` strictly, so the platform must
  substitute `internet_ip` with the real host (`W9_URL_REPLACE=true`). An underscore placeholder
  such as `internet_ip` is rejected by Moodle's URL validation.
- The elestio image sets `$CFG->sslproxy = true` for its TLS proxy. This package serves plain HTTP,
  so `src/disable-sslproxy.sh` removes that line after install.

