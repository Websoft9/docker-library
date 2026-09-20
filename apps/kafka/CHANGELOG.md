# CHANGELOG

## 2026-09-13

- Updated Kafka from `4.0.1` to `4.3.1` and limited supported versions to the 4.x line.
- Enriched `upstream` with releases, the official single-node compose, and Kafka docs.
- Parameterized the KRaft node id, controller quorum voters, and advertised listeners so the package can be extended to a cluster.
- Standardized the broker port variable to `W9_MQ_PORT_SET` and added `KAFKA_ADVERTISED_HOST` for the external advertised address.
- Fixed a platform install failure (`Initialize repo error`): removed `W9_URL` / `W9_URL_REPLACE`, which made the Websoft9 platform treat Kafka as a web app and require a web port.
- Added a broker healthcheck and documented cluster preparation in `Notes.md`.
- Documented the 9092 / 19092 / 29093 listeners in `.env` and `docker-compose.yml`, making clear that only the external listener is published.
- Added repo catalog commercial metadata at `metadata/catalog/kafka.json`.
- Regenerated `README.md` from `variables.json` and `docker-compose.yml`.

## 4.0.1

- Migrated from `bitnamilegacy/kafka` to official `apache/kafka` image
- Updated supported versions: `4.0.1`, `3.9.2`, `3.8.1`, `3.7.2`
