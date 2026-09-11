# CHANGELOG

## 2026-09-11
- Updated the default PostgreSQL version from `17` to `18` and added `18` to the supported version list.
- Kept the data volume at `/var/lib/postgresql/data` and pinned `PGDATA=/var/lib/postgresql/data` for every version. PostgreSQL 18 defaults to a version-specific path (`/var/lib/postgresql/18/docker`), so pinning `PGDATA` avoids the v18 layout change and keeps one consistent persisted path across 14-18.
- Moved the `POSTGRES_*` variables into `.env` and normalized `.env` / `docker-compose.yml` to current repository policy rules (braced `${VAR}` references, port purpose comment, removal of the obsolete `version` and source comments).
- Expanded `upstream` metadata with the official release and documentation sources.
- Regenerated the README.
