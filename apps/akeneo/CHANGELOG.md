# CHANGELOG

## 2026-11-05

- Limited final image-build and post-initialization ownership changes to the writable `var` directory; source and frontend dependencies already belong to `www-data`.
- Avoided redundant recursive ownership changes across `node_modules`, which exceeded the remote test build budget.
- Kept database connections, image versions, and source dependencies unchanged.
- Verified remote image build, fresh initialization, login-page access, and database-marker preservation after retained-volume recreation. Full baseline migration requires a separately built baseline image; Owner E2E and external MySQL tests remain pending.

## 2026-11-04

- Declared internal MySQL and unauthenticated Elasticsearch dependencies, retaining the existing APP_DATABASE_* inputs shared by web and worker.
- Separated bundled MySQL initialization into independent MYSQL_* defaults and declared external MySQL inputs.
- Image versions and default connections are unchanged; static configuration checks passed, but deployment and live connection validation were not performed.

## 2026-10-13
- Added `tests/cases.yml` coverage for the Akeneo login page so deploy validation exercises the real web entry path instead of only default checks.
- Hardened the Docker image package-install step with an apt index refresh retry to avoid transient Debian mirror 404 failures during build.

## 2026-09-03
- Rebuilt the Akeneo package around a custom Dockerfile based on `akeneo/pim-php-dev:8.3`.
- Updated Akeneo to `v2026.4` with a build-time `composer create-project` flow instead of runtime source installation.
- Updated bundled dependencies to MySQL 8.4 and Elasticsearch 8.17.0.
- Added a `worker` service running the messenger consumers for `ui_job`, `import_export_job`, and `data_maintenance_job`.
- Added first-startup creation of the Akeneo admin user from `AKENEO_ADMIN_USER` / `AKENEO_ADMIN_PASSWORD`.
- Stopped re-running `pim:installer:assets` at container startup so the built-in `public/css|js|dist` assets are no longer wiped (fixed broken login-page styling and post-login loading).
- Moved the Dockerfile to the app root (`apps/akeneo/Dockerfile`) and made `docker-compose.yml` pull-only (no `build` block); shared app/worker config moved to a `x-` anchor.
- `libs app-deploy` now delegates image builds to the shared `libs app-build` implementation, so pull-only custom-image apps are built on the target host before `up -d`.
- Regenerated the README via the app generator.
