# CHANGELOG

## 2026-10-13
- Update CKAN from `2.11.0` to `2.12.0` and align the Solr and PostgreSQL dependency tags with the upstream 2.12 stack.
- Normalize `.env` and `docker-compose.yml` variable references to `${VAR}` syntax and refresh upstream metadata sources.
- Add app-specific validation coverage for the CKAN login page and replace the placeholder changelog format with the repository-standard date heading.
## 2026-10-13

- aligned CKAN PostgreSQL environment with the upstream `ckan-postgres:2.12` role/database naming (`ckan_default`, `datastore_write`, `datastore_read`) so the app and bundled database image bootstrap the same credentials
- switched the bundled database service from `ckan/ckan-postgres-dev:2.12` to plain `postgres:16` plus app-local init scripts, because the upstream dev image ships preloaded `/data` state that prevented clean validation reinitialization and kept rejecting the packaged credentials
