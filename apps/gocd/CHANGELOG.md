# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-13

- Updated GoCD server and agent from `v25.3.0` to `v26.1.0`.
- GoCD publishes only `vX.Y.0` tags, so `v26.1.0` is the correct stable target.
- Server and agent images stay aligned through the shared `W9_VERSION` variable.

## Release
### Fixes and Enhancements
