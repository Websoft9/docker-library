# CHANGELOG

## 2026-10-12

- Replaced the incorrect WordPress/MariaDB package with the official LiteLLM proxy self-hosting topology.
- Pinned the main image to `ghcr.io/berriai/litellm:v1.105.0` and added bundled PostgreSQL for DB-backed model and key management.
- Added persistent proxy configuration and package metadata for the `/ui` admin console.
- Configured explicit `UI_USERNAME` and `UI_PASSWORD` so the Admin UI does not require using the master key for environment-credential login.
