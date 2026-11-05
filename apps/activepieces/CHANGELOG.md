# Changelog

## 2026-11-04

- Separated bundled PostgreSQL initialization from `AP_POSTGRES_*` application inputs, preserving the original database, user, and password seed; removed unnecessary application env-file injection into PostgreSQL.
- Declared external PostgreSQL using the five existing native inputs shared by app and worker; retained internal Redis and the fixed PostgreSQL driver.
- Preserved images, volumes, commands, and startup dependencies; verified default/override configuration and initialization isolation statically without deployment or live database verification.

## 2026-10-13

- Upgraded Activepieces from `0.88.4-hotfix.1` to `0.92.3`.
- Fixed `AP_FRONTEND_URL` to use `http://${W9_URL}` so the packaged public URL matches upstream self-host requirements and repository URL wiring rules.

## 2026-08-27

- Upgraded Activepieces from `0.70.4` to `0.88.4`.
- Switched the package to the official four-container deployment shape: app, worker, PostgreSQL, and Redis.
- Added a dedicated worker service with `AP_CONTAINER_TYPE=WORKER` and an internal `AP_FRONTEND_URL` override so the worker can reach the app container.
- Updated the PostgreSQL dependency to the pgvector PostgreSQL 14 image line used by the upstream Docker Compose deployment.
- Added a main-container healthcheck and app tests covering the `/api/v1/health` endpoint.
- Aligned metadata with the upstream compose and env example sources, and regenerated the app README.
- Upgraded Activepieces from `0.88.4` to `0.88.4-hotfix.1`.
- Declared `W9_URL_REPLACE=true` because the package uses `AP_FRONTEND_URL=$W9_URL` during install/runtime URL configuration.
