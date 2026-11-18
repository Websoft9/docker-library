# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-13

- Upgrade CouchDB community from `3.5.0` to the stable `3.5` track, verified against upstream Apache tags through `3.5.3`.
- Normalize the package to current repository conventions for `.env` layout, braced variable references, and documented published port purpose.
- Add app-specific authenticated validation coverage for the CouchDB HTTP API.
