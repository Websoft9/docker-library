# CHANGELOG

## 2026-09-02

- Update Airflow from 3.1.0 to 3.3.1.
- Bump the bundled PostgreSQL from 13 to 18 (highest major Airflow 3.3.1 is tested against), now driven by `W9_DB_VERSION`.
- Remove legacy `# docs:` / `# image:` source comments from `docker-compose.yml`, use braced `${VAR}` references, and add an inline `# Web Console` purpose comment to the published port.
- Add a minimal README note that upgrading across Airflow/PostgreSQL majors is a data migration.

