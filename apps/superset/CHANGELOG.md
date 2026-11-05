# CHANGELOG

## 2026-11-05

- Verified fresh deployment, retained-volume recreation, and database-declaration baseline-to-current configuration migration on the new remote test server.
- Web and worker health checks passed, initialization exited successfully, and the PostgreSQL test marker survived recreation and migration.
- Owner login, chart/dataset workflows, and external PostgreSQL acceptance remain pending; no image upgrade was performed.

## 2026-11-04

- Declared one PostgreSQL instance with the main, examples, and script-created superset_cypress databases plus separate main and examples account sources.
- Separated main and examples database initialization from application connection inputs and declared external PostgreSQL inputs for all four consumers.
- Kept Redis internal and unauthenticated with the current logical database defaults; image versions and default connections are unchanged.
- Added the executable 6.1.0 healthcheck script hidden by the mounted docker directory.
- Install PostgreSQL dependencies only when the driver is missing, including for workers using the lean release image.
- Disabled optional example data loading by default; database migrations, administrator creation and role initialization remain enabled. Existing example data is not deleted.
- Verified remote Compose recreation: web and worker healthy, beat running, initializer exited successfully, and the database container and test marker preserved. Full baseline migration and Owner E2E remain separate acceptance steps.

## 2026-09-17

- update Superset from 4.1.1 to 6.1.0
- align `.env` and `docker-compose.yml` with current repository env policy and startup ordering
- refresh Superset docker bootstrap/config files for 6.1.0 compatibility
