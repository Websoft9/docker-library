# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-09
- update OpenSearch from 3 to 3.9.0 and add first-start-only password metadata
- align compose variable references, published port comments, and health check wiring with current policy
- add a smoke test for OpenSearch Dashboards and document the `vm.max_map_count` prerequisite
