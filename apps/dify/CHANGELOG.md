# CHANGELOG

## 2026-11-17

- Updated Dify to 1.19.0 with the matching Agent backend, local sandbox, WebSocket API, plugin daemon, and code sandbox images.
- Added the Agent sandbox authentication secrets, protected proxy path, and storage permission initialization required by the upstream deployment.
- Updated bundled Weaviate to 1.39.13; existing installations must follow Dify's staged Weaviate upgrade path before starting this version.

## 2026-11-04

- Declared one PostgreSQL component with main/plugin database names, authenticated internal Redis, and internal Weaviate; API keys are not account/password metadata.
- Kept all stores internal-only; removed the external PostgreSQL provider and connection mappings, recorded the default postgres account without adding initialization variables solely for metadata.
- Restored initialization references to the original application values while preserving current native consumer wiring and normalized variable references rather than reverting user changes.
- Removed unnecessary application env-file injection into PostgreSQL and Redis, preserved explicit Redis authentication, and normalized variable references without changing images.
- Resolved the access-port false positive in the shared validator, preserving the existing port mapping. Static configuration checks passed without deployment or live database verification.

## Release
### Fixes and Enhancements
