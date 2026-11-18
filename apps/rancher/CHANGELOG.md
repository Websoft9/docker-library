# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-09-30

- Pin Rancher community from the floating `latest` alias to `v2.15.2`.
- Model the console as an HTTPS port (`W9_HTTPS_PORT_SET`) instead of `W9_HTTP_PORT_SET`.
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, and the current `.env` layout.
- Add a self-signed HTTPS reachability check in `tests/cases.yml`.
