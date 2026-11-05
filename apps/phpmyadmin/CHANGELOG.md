# CHANGELOG

## 2026-11-04

- Moved the optional database root password to `MYSQL_ROOT_PASSWORD` backed by `W9_POWER_PASSWORD`, preserving the existing default without rotating installed credentials.
- Added the `mysql` network alias and declared the optional internal MariaDB dependency; the `db` profile remains disabled by default.
- Image versions are unchanged; deployment and live connection validation were not performed.

## 2026-09-14

- Declared `variables.json.access` for the app (`web`, port 80) and the `/phpmyadmin/` path (`admin`, port 80).
- Updated phpMyAdmin to the `5.2` line; pinned `W9_VERSION` from the floating `latest` alias and listed `5.2` in `variables.json.edition`.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image source comment, and no obsolete compose `version` key.
- Added `upstream.docs` and a phpMyAdmin login-page check in `tests/cases.yml`.
