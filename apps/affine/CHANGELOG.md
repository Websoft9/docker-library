# CHANGELOG

## 2026-10-13

- Verified upstream stable remains 0.27.4; removed the unsupported `latest` version claim from package metadata.
- Marked `W9_POWER_PASSWORD` as first-startup-only because bundled PostgreSQL applies its initialization auth settings only on a fresh data directory.
- Added app-specific AFFiNE smoke coverage under `tests/cases.yml` to validate the first-run landing page beyond the default adaptive checks.

## 2026-08-29

- Rebuilt the package on upstream 0.27.4 compose: main app + one-time `affine-migration` job, `pgvector/pgvector:pg16` Postgres, and Redis.
- Config moved `server.externalUrl` driven by `W9_URL` from `config/config.json` (mounted from `src/config.json`) to `.env` vars
- Enabled Postgres password authentication via `$W9_POWER_PASSWORD` and declared `W9_DB_EXPOSE` and `database` metadata so users can maintain the database with credentials.
- Fixed package structure: valid compose services, `.env`, `src/`, and release metadata; upstream image corrected to `ghcr.io/toeverything/affine`.
