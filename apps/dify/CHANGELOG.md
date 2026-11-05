# CHANGELOG

## 2026-11-04

- Declared one PostgreSQL component with main/plugin database names, authenticated internal Redis, and internal Weaviate; API keys are not account/password metadata.
- Kept all stores internal-only; removed the external PostgreSQL provider and connection mappings, recorded the default postgres account without adding initialization variables solely for metadata.
- Restored initialization references to the original application values while preserving current native consumer wiring and normalized variable references rather than reverting user changes.
- Removed unnecessary application env-file injection into PostgreSQL and Redis, preserved explicit Redis authentication, and normalized variable references without changing images.
- Resolved the access-port false positive in the shared validator, preserving the existing port mapping. Static configuration checks passed without deployment or live database verification.

## Release
### Fixes and Enhancements

