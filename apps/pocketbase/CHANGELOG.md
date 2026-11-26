# CHANGELOG

## 2026-11-26

- Split installation guidance into `help.init` (superuser created on first start, pre-1.0 upgrade caveat) and `help.login` (sign-in steps).

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-09-28

- Add declarative `variables.json.credentials.username` / `password` metadata for PocketBase while keeping legacy `W9_LOGIN_GET_PASSWORD` for compatibility.

## 2026-10-09

- Updated PocketBase from `v0.29.1` to `v0.40.5`.
- Replaced inconsistent third-party image references with a package-local image built from the official PocketBase release binary.
- Refreshed package metadata, healthcheck, and admin-console test coverage.

## Release
### Fixes and Enhancements
