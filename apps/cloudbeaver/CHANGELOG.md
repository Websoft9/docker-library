# CHANGELOG

## 2026-09-17

- Updated `W9_VERSION` from `25.2.2` to `26.2` and aligned `variables.json.edition` with the current upstream `x.x` tag.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image/docs source comments, and no obsolete compose `version` key.
- Added `W9_URL_REPLACE=true` because `CB_SERVER_URL` references `W9_URL`.
- Added `upstream.docs`, `variables.json.access`, and `env.first_startup_only`; regenerated the README.
