# CHANGELOG

## 2026-09-14

- Pin SonarQube Community Build to `26.9.0.129388-community` (alias `latest`).
- Add `upstream` metadata: image, releases, official compose, and docs.
- Add `W9_DB_VERSION=17` and parameterize the bundled PostgreSQL image.
- Add `tmpfs` for `/tmp`, required by SonarQube 2026.x Elasticsearch under `read_only`.
- Normalize environment references to the braced `${VAR}` form and remove source comments from `docker-compose.yml`.
- Add `tests/cases.yml` with a system-status check and repository catalog data.
