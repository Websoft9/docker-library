# CHANGELOG

## 2026-10-15

- Restored the archived `inngest` package to active maintenance and rebuilt it into a real Inngest self-hosted server package based on the official self-hosting docs and Docker image.
- Replaced the leftover WordPress template content in `.env` and `docker-compose.yml` with Inngest services: the main server (`inngest start`) plus bundled PostgreSQL 17 and Redis 7.
- Declared `INNGEST_EVENT_KEY` and `INNGEST_SIGNING_KEY` as package secrets, wired `INNGEST_POSTGRES_URI` and `INNGEST_REDIS_URI` to the bundled services, and added the official `inngest alpha doctor healthcheck` for the main container.
- Added the `/health` app-specific validation check and refreshed `variables.json` and the generated README.
- Fixed the Postgres wiring so the user and database are the fixed name `inngest` in both `INNGEST_POSTGRES_URI` and the bundled `postgres` service. The connection string no longer depends on `${W9_ID}`, so an instance renamed by the platform (for example `inngest_ssozr`) still authenticates.
