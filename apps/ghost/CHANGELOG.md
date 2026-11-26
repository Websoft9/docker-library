# CHANGELOG

## 2026-11-26

- Split installation guidance into `help.init` (first-start prerequisites) and `help.login` (sign-in steps).

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-03
- Declared the MySQL dependency and existing native connection inputs; kept the fixed database client and runtime configuration unchanged.
- Recorded the existing bundled MySQL 8.0 EOL risk separately from declaration validation; no database upgrade was performed.

## 2026-10-13
- Updated Ghost community to 6.69.
- Regenerated the README.

## 2026-09-29

- Update Ghost community to 6.65.
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, dead variable cleanup, and refreshed metadata.
- Add an app-specific admin console check in `tests/cases.yml`.
