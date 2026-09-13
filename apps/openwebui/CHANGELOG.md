# CHANGELOG

## 2026-09-13
- Pinned the Open WebUI image to `0.11`; `main` is kept only as a rolling test option and is not guaranteed.
- Dropped the `cuda` edition and removed `docker-compose-gpu.yml`; added a note explaining the CUDA variant is out of scope for this package.
- Made `ollama` and `chroma` optional Docker Compose profiles that are not started by default and publish no host ports.
- Added a main-container healthcheck based on the image's `/health` endpoint.
- Enriched `variables.json` `upstream` with releases and docs.
- Added `tests/cases.yml` with a `/health` functional check.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
