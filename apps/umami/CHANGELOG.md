# CHANGELOG

## 2026-09-20

- Update Umami to 3.4 and switch the image to the official `ghcr.io/umami-software/umami`.
- Add `TWO_FACTOR_ENCRYPTION_KEY` required by two-factor authentication.
- Model the bundled PostgreSQL version with `W9_DB_VERSION` and wait for a healthy database before starting the app.
- Default the web port to 9003; refresh `variables.json`, README, Notes and add a login/health test.
