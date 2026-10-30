# CHANGELOG

## 2026-10-30

- Updated Metabase to the official `v0.64-lts` Docker image tag.

## 2026-10-23

- Updated Metabase to the official `v0.64.1.x` Docker image tag from the invalid `v0.64.x` placeholder.
- Updated version metadata so upstream scans can parse and compare the current Metabase image correctly.

## 2026-10-08

- Updated Metabase from `v0.57.5.3` to `v0.64.x`.
- Updated bundled PostgreSQL from `13` to `14` for Metabase 0.64 compatibility.
- Normalized `.env` and `docker-compose.yml` to current repository policy requirements.
- Added app-specific validation coverage for the Metabase setup path.
