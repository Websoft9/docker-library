# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-09-21

- Update Traefik from `v3.6` to `v3.7`.
- Make the packaged Websoft9 entrypoint target the Traefik dashboard on port `8080` and expose the proxy HTTP entrypoint separately.
- Align app metadata and validation coverage with current repository rules.
