# CHANGELOG

## 2026-09-13

- Updated Redpanda Console from `v3.1.3` to `v3.12.0`.
- Fixed broker pairing: the default broker is now the Kafka package's internal listener `kafka:19092` instead of the non-existent `kafka_yhmk4:9092`.
- Removed the invalid Schema Registry configuration that pointed at the broker.
- Enriched `upstream` with releases and the Console configuration reference.
- Added `access` metadata, a container healthcheck, `tests/cases.yml`, and repo catalog data.
- Documented that the OSS Console requires a configured broker and cannot add clusters from the UI, and that `KAFKA_STARTUP_MAXRETRIES=0` must not be used (it hangs startup in v3.12.0).
- Regenerated `README.md` from `variables.json` and `docker-compose.yml`.

## Release

### Fixes and Enhancements
