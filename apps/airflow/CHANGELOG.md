# CHANGELOG

## 2026-11-05

- Routed DAG processor, triggerer and worker health probes through the image entrypoint so the configured root UID receives the same Python package path as the running services.
- Kept the existing probe timeout, UID, database inputs, images and volumes unchanged.
- Remote fresh install, all required service health checks, retained-data recreation and same-version baseline configuration migration passed. Owner E2E and external database connections were not tested.

## 2026-11-04

- Wired both native PostgreSQL URLs through `.env` for all seven Airflow consumers, keeping bundled initialization independent.
- Declared internal/external PostgreSQL and the internal unauthenticated Redis broker; preserved image versions, startup dependencies and data volumes.
- Deployment and live connection validation were not performed.

## 2026-10-13

- Update Airflow from 3.3.1 to 3.3.2.
- Add a minimal app-specific functional check for the version API endpoint.

## 2026-09-02

- Update Airflow from 3.1.0 to 3.3.1.
- Bump the bundled PostgreSQL from 13 to 18 (highest major Airflow 3.3.1 is tested against), now driven by `W9_DB_VERSION`.
- Remove legacy `# docs:` / `# image:` source comments from `docker-compose.yml`, use braced `${VAR}` references, and add an inline `# Web Console` purpose comment to the published port.
- Add a minimal README note that upgrading across Airflow/PostgreSQL majors is a data migration.
