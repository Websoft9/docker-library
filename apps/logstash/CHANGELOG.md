# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-12

- Updated the main image from `docker.elastic.co/logstash/logstash:9.1.0` to `docker.elastic.co/logstash/logstash:9.5.5`.
- Added an app-specific API reachability test for the Logstash monitoring endpoint.
- Refreshed the generated package README so the supported version matches the updated image tag.
