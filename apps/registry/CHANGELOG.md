# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-08

- Updated Docker Registry from `3.0` to `3.1`.
- Normalized `.env` and `docker-compose.yml` to current repository policy requirements.
- Added app-specific validation coverage for the Registry v2 API path.
- Clarified that `src/` currently contains reference-only files and is not mounted by default.
