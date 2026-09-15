# CHANGELOG

## 2026-09-15

- Update Checkmate to `v3.12.0` and pin the mono image `ghcr.io/bluewave-labs/checkmate`.
- Switch the bundled database to the official `mongo:8.2` image via `W9_DB_VERSION` (the legacy `checkmate-mongo` image has no 3.12 tag, and MongoDB 8.0 refuses to start on Linux kernel 6.19+).
- Add the upstream `/livez` healthcheck to the app service.
- Align environment variables with upstream: `DB_CONNECTION_STRING`, `CLIENT_HOST`, and a generated `JWT_SECRET`; add `W9_URL_REPLACE` so `CLIENT_HOST` gets the public URL.
- Add `upstream` metadata (releases, compose, env example, docs), `tests/cases.yml`, and repository catalog data.
