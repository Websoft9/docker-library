# CHANGELOG

## 2026-09-12

- Updated Chroma from `1.3.5` to `1.5.9`, the latest stable upstream release.
- Aligned `.env` and `docker-compose.yml` with current repository policy, including braced variable references and inline published-port comments.
- Removed the unused custom `/config.yaml` mount and followed the upstream default persistent data path at `/data`.
- Added upstream references for releases, compose, and deployment documentation in `variables.json`.
