# CHANGELOG

## 2026-09-20

- Updated Weaviate from `1.26.6` to `1.39.5`, the latest stable upstream release.
- Pinned `W9_VERSION` to `1.39.5` and declared it in `variables.json`.
- Added the gRPC API port (`W9_GRPC_PORT_SET`, 50051) required by Weaviate clients.
- Removed `ENABLE_API_BASED_MODULES`, which upstream removed in v1.33.
- Aligned `.env` and `docker-compose.yml` with current repository policy: braced variable references, inline published-port comments, and the `.env` section banner with a Docs URL.
- Added a readiness healthcheck against `/v1/.well-known/ready`.
- Added `tests/cases.yml` with an app-specific readiness check.
- Added upstream releases and documentation references to `variables.json`.
- Regenerated `README.md`.
