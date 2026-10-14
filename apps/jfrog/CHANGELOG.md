# CHANGELOG

## 2026-10-13
- Initial JFrog Artifactory community package based on the official `releases-docker.jfrog.io/jfrog/artifactory-pro` image.
- Add `docker-compose.yml` publishing the JFrog Platform console on `${W9_HTTP_PORT_SET}:8082`, with the `jfrog_data` volume at `/var/opt/jfrog/artifactory` and a `/router/api/v1/system/health` healthcheck.
- Enable the embedded Derby database via `JF_SHARED_DATABASE_TYPE=derby` and `JF_SHARED_DATABASE_ALLOWNONPOSTGRESQL=true` so no external database is required.
- Declare the built-in `admin` / `password` credentials with a first-sign-in password-change note in `help.login`.
- Fill `.env`, `variables.json`, `README.md`, and add `tests/cases.yml` with an Artifactory ping check.
