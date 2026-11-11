# CHANGELOG

## 2026-11-11

- Use the stable `2.4` image tag instead of pinning the patch and Debian variant; it currently resolves to the same image as `2.4.4-bookworm-slim`.

## 2026-11-09

- Restore the app package and align it with current repository conventions.
- Pin `2.4.4-bookworm-slim`, then-current upstream image tag, and refresh `upstream` metadata.
- Publish the web admin console and declare the web access surface plus database credentials.
- Remove the obsolete Compose `version` key and source comments, use braced `${VAR}` references, and add a driver-port healthcheck.
- Make first-run initialization idempotent so restarts skip `rethinkdb create` when data already exists.
- Record the first-startup-only admin password and add a driver-port smoke test.
