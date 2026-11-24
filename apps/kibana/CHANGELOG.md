# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-04

- Declared optional external Elasticsearch through the officially supported `ELASTICSEARCH_HOSTS` JSON array passed via the existing env-file path.
- Kept the default backend unconfigured and the sample commented out; no Elasticsearch service is added and service-account tokens are not database passwords.
- Left runtime files unchanged; verified native host-array and token delivery statically without deployment or live Elasticsearch verification.

## 2026-10-12

- Updated Kibana from `8.12.2` to `9.5.5` because the Elastic registry does not publish a usable `9.5` tag for this image.
- Normalized `.env` and `docker-compose.yml` to current repository conventions, including braced variable references and inline port purpose comments.
- Added upstream docs metadata and an app-specific admin UI test case.
