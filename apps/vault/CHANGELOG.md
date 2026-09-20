# CHANGELOG

## 2026-09-20

- Updated Vault from `1.21` to `2.1`, the latest stable upstream minor (upstream `2.1.1`).
- Pinned `W9_VERSION` to `2.1` and declared it in `variables.json`.
- Kept the package in Vault dev mode (`server -dev`), matching the current image default.
- Replaced the legacy `W9_LOGIN_GET_TOKEN` hint with a declarative `variables.json.credentials.password` source (`container-log`, pattern `Root Token:`).
- Aligned `.env` and `docker-compose.yml` with current repository policy: braced variable references, inline published-port comment, and the `.env` section banner with a Docs URL.
- Removed the obsolete `version:` key and the `# image:` / `# docs:` source comments; moved `VAULT_LOCAL_CONFIG` into `.env`.
- Added a healthcheck against `/v1/sys/health`.
- Added `tests/cases.yml` with a Vault health check.
- Added upstream releases and documentation references to `variables.json`.
- Regenerated `README.md`.
