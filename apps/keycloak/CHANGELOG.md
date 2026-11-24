# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-12

- Updated Keycloak from `26.4` to `26.8`.
- Normalized `.env` and `docker-compose.yml` to current repository conventions, including braced variable references and inline port purpose comments.
- Added `tests/cases.yml` to cover the admin console path for automated validation.
