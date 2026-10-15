# CHANGELOG

## 2026-09-17

- Updated `W9_VERSION` from `latest` to `v3.57.1` and aligned `variables.json.edition` with the current upstream tag.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, and no image/docs source comments.
- Added `DATABASUS_URL` wired to `W9_URL` and set `W9_URL_REPLACE=true`.
- Added `upstream.docs`, `upstream.releases`, and `variables.json.access`; added `tests/cases.yml` with the system health check; generated the README.
