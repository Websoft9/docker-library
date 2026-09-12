# CHANGELOG

## 2026-09-11
- Updated the supported version list to `18` and `latest` only, dropping the older majors (`9.6`-`17`).
- Changed the data volume to the official PostgreSQL 18 layout: mount `postgres` at `/var/lib/postgresql` and rely on the image default `PGDATA=/var/lib/postgresql/18/docker`.
- Documented the PostgreSQL 17 and below data path (`/var/lib/postgresql/data`) in `.env`, `docker-compose.yml`, and the README.
- Added concise major-version upgrade steps to the README.
- Moved the `POSTGRES_*` variables into `.env` and normalized `.env` / `docker-compose.yml` to current repository policy rules (braced `${VAR}` references, port purpose comment, removal of the obsolete `version` and source comments).
- Expanded `upstream` metadata with the official release and documentation sources.
- Regenerated the README.
