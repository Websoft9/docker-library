# CHANGELOG

## 2026-11-03

- Declared the PostgreSQL dependency and existing DATABASE_URL input, keeping the fixed database type out of connection mappings.
- Distinguished the PostgreSQL initialization/administration account from the script-created umami application account whose password comes from W9_RCODE.
- Kept the initialization script, runtime configuration, and image versions unchanged.

## 2026-09-20

- Update Umami to 3.4 and switch the image to the official `ghcr.io/umami-software/umami`.
- Add `TWO_FACTOR_ENCRYPTION_KEY` required by two-factor authentication.
- Model the bundled PostgreSQL version with `W9_DB_VERSION` and wait for a healthy database before starting the app.
- Default the web port to 9003; refresh `variables.json`, README, Notes and add a login/health test.
