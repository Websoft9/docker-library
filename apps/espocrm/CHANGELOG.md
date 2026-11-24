# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-03
- Declared the MariaDB dependency and existing connection inputs shared by the web and daemon services without changing runtime configuration.
- Recorded the existing bundled MariaDB 10.6 EOL risk separately from declaration validation; no database upgrade was performed.

## 2026-09-30

- Updated EspoCRM from `9.2.2` to `10.0`.
- Normalized `.env` and `docker-compose.yml` to current repository policy.
- Recorded first-startup-only admin and site URL settings.
- Migrated volume mounts for EspoCRM 10 so image-provided application files are no longer shadowed by a full `/var/www/html` volume.
- Added app-specific validation coverage for the installer path.
