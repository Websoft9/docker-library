# CHANGELOG

## 2026-09-03
- Rebuilt the Akeneo package around a custom Dockerfile based on `akeneo/pim-php-dev:8.3`.
- Updated Akeneo to `v2026.4` with a build-time `composer create-project` flow instead of runtime source installation.
- Updated bundled dependencies to MySQL 8.4 and Elasticsearch 8.17.0.
- Added a `worker` service running the messenger consumers for `ui_job`, `import_export_job`, and `data_maintenance_job`.
- Added first-startup creation of the Akeneo admin user from `AKENEO_ADMIN_USER` / `AKENEO_ADMIN_PASSWORD`.
- Stopped re-running `pim:installer:assets` at container startup so the built-in `public/css|js|dist` assets are no longer wiped (fixed broken login-page styling and post-login loading).
- Regenerated the README via the app generator.
