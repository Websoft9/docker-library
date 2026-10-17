# CHANGELOG

## 2026-10-15
- Switch the main image from the Pro edition to the open source `releases-docker.jfrog.io/jfrog/artifactory-oss`; Artifactory OSS requires no license.
- Update `.env` (`W9_REPO`), `variables.json` (`upstream.image`, `help.login`), and `README.md` (image references, remove license notes).
- Add `JF_JFCONNECT_ENABLED=false`: the OSS image lacks the JFrog Connect service, and leaving it enabled makes the frontend entitlement client loop on a missing endpoint so the login screen never finishes loading.

## 2026-10-13
- Initial JFrog Artifactory community package based on the official `releases-docker.jfrog.io/jfrog/artifactory-pro` image.
- Add `docker-compose.yml` publishing the JFrog Platform console on `${W9_HTTP_PORT_SET}:8082`, with the `jfrog_data` volume at `/var/opt/jfrog/artifactory` and a `/router/api/v1/system/health` healthcheck.
- Enable the embedded Derby database via `JF_SHARED_DATABASE_TYPE=derby` and `JF_SHARED_DATABASE_ALLOWNONPOSTGRESQL=true` so no external database is required.
- Declare the built-in `admin` / `password` credentials with a first-sign-in password-change note in `help.login`.
- Fill `.env`, `variables.json`, `README.md`, and add `tests/cases.yml` with an Artifactory ping check.
