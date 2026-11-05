# CHANGELOG

## 2026-11-05

- Replaced unsupported session/JWT placeholders with two consumer-compatible random seed templates.
- Declared `CKAN_API_TOKEN_SECRET` and made JWT encode/decode reference the same seed, preserving the required `string:` wrapper rather than independently generating both settings.
- Added template/reference checks and installation-retry verification against the existing Websoft9 consumer; existing instance keys must be preserved, not rotated from package defaults.
- Remote fresh installation and retained-data recreation passed with consumer-generated settings: all five services healthy, API token creation/authentication passed, the same token remained usable after recreation, and keys/database marker were retained. Owner E2E and real-instance rotation were not tested.

## 2026-11-04

- Declared PostgreSQL, Solr, and unauthenticated Redis as three distinct dependencies; excluded the API-based Datapusher service.
- Recorded main, datastore, and script-created test databases plus separate bootstrap, main, write, and read accounts.
- Mapped the three existing production PostgreSQL URLs without selecting an account or database in metadata; preserved their postgresql:// prefix.
- Kept initialization scripts, runtime configuration, and image versions unchanged.

## 2026-10-13
- Update CKAN from `2.11.0` to `2.12.0` and align the Solr and PostgreSQL dependency tags with the upstream 2.12 stack.
- Normalize `.env` and `docker-compose.yml` variable references to `${VAR}` syntax and refresh upstream metadata sources.
- Add app-specific validation coverage for the CKAN login page and replace the placeholder changelog format with the repository-standard date heading.
## 2026-10-13

- aligned CKAN PostgreSQL environment with the upstream `ckan-postgres:2.12` role/database naming (`ckan_default`, `datastore_write`, `datastore_read`) so the app and bundled database image bootstrap the same credentials
- switched the bundled database service from `ckan/ckan-postgres-dev:2.12` to plain `postgres:16` plus app-local init scripts, because the upstream dev image ships preloaded `/data` state that prevented clean validation reinitialization and kept rejecting the packaged credentials
