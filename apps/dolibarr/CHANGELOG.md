# CHANGELOG

## 2026-09-17

- Fixed the version drift: pinned `W9_VERSION` from `18` to `19.0.2`, matching `variables.json.edition` and the current upstream release.
- Replaced the non-standard `W9_MARIADB_VERSION` with `W9_DB_VERSION` and pinned the bundled MariaDB to `12.3` (LTS); `11.4` and `11.8` were also verified against Dolibarr 19.0.2.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image/docs source comments, and no obsolete compose `version` key.
- Replaced the legacy `links` dependency with the shared `websoft9` network plus `depends_on`.
- Added `upstream.docs`, `variables.json.access`, `help.db`, and a login-page functional check in `tests/cases.yml`.
- Regenerated the README.
