# CHANGELOG

## 2026-09-21

- Switch Trivy from CLI shell mode to **server mode** (`trivy server --listen 0.0.0.0:4954`).
- Bump `aquasec/trivy` from `0.68.1` to `0.74.0`.
- Publish the server API on `${W9_HTTP_PORT_SET}` and persist the vulnerability database in the `trivy_cache` volume.
- Enable token authentication through `TRIVY_TOKEN`, carried by `W9_LOGIN_PASSWORD` so the interface can display it.
- Add a `/healthz` healthcheck and an app-specific `tests/cases.yml`.
- Remove the unused scan-path mount (`W9_SCAN_PATH_SET`) that only applied to the CLI shell mode.
