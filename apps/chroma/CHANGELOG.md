# CHANGELOG

## 2026-09-13

- Added repo catalog commercial metadata at `metadata/catalog/chroma.json`.
- Added `tests/cases.yml` with a heartbeat check against `/api/v2/heartbeat`.
- Published the HTTP API through `W9_HTTP_PORT_SET` so the standard test and validation flow can reach the app.
- Matched the official 1.5.9 healthcheck (`curl` against `/api/v2/heartbeat`) and `unless-stopped` restart policy.
- Regenerated `README.md` from `variables.json` and `docker-compose.yml`.

## 2026-09-12

- Updated Chroma from `1.3.5` to `1.5.9`, the latest stable upstream release.
- Aligned `.env` and `docker-compose.yml` with current repository policy, including braced variable references and inline published-port comments.
- Removed the unused custom `/config.yaml` mount and followed the upstream default persistent data path at `/data`.
- Added upstream references for releases, compose, and deployment documentation in `variables.json`.
