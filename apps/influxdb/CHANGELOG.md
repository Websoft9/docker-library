# CHANGELOG

## 2026-09-14
- Updated InfluxDB to `2.9`; `latest` now resolves to the 2.9 line.
- Added a main-container healthcheck on `/health`.
- Added `tests/cases.yml` with a `/health` functional check.
- Replaced the unused `influxdb2-config` volume with a read-only `./src/config.yml` mount at `/etc/influxdb2/config.yml`, so configuration is declared in the package instead of only documented.
- Removed the obsolete `Notes.md`; the configuration guidance now lives in `src/config.yml` and the README.
- Added the InfluxDB 3 Core variant: the `3-core` edition with `docker-compose.3-core.yml` and `.env.3-core` (HTTP API on `8181`, data in the `influxdb3-data` volume).
- Enriched `variables.json` `upstream` with releases and both InfluxDB 2.x and 3.x docs.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
