# CHANGELOG

## 2026-09-15

- Update Prometheus to `v3.14.0` (alias `latest`).
- Pin bundled sidecars: `prom/pushgateway:v1.11.3` and `prom/alertmanager:v0.34.0`.
- Add `upstream` metadata: releases and docs.
- Remove the obsolete `version:` key and source comments from `docker-compose.yml`, normalize references to `${VAR}`, and add a port purpose comment.
- Add `tests/cases.yml` with a readiness check and repository catalog data.
