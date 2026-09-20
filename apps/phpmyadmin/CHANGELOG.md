# CHANGELOG

## 2026-09-14

- Declared `variables.json.access` for the app (`web`, port 80) and the `/phpmyadmin/` path (`admin`, port 80).
- Updated phpMyAdmin to the `5.2` line; pinned `W9_VERSION` from the floating `latest` alias and listed `5.2` in `variables.json.edition`.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image source comment, and no obsolete compose `version` key.
- Added `upstream.docs` and a phpMyAdmin login-page check in `tests/cases.yml`.
