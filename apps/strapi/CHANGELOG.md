# CHANGELOG

## 2026-09-22
- Rebuild the Strapi package from the official Strapi 5 npm distribution because upstream no longer publishes official container images.
- Replace the legacy Strapi 3 + MySQL package with a self-built Strapi 5.54.0 application on Node 22.
- Switch storage to bundled SQLite persisted in `strapi_data`, and persist uploads separately in `strapi_uploads`.
- Auto-create the first administrator on first start from `W9_LOGIN_USER` and `W9_LOGIN_PASSWORD`.
- Add `tests/cases.yml` to validate the Strapi admin route instead of the root path.
- Note: this package is for fresh Strapi 5 deployments; existing Strapi 3 data is not a drop-in in-place upgrade target.

## 2026-09-23
- Remove the `build` section from `docker-compose.yml` so runtime deployment consumes a prebuilt `websoft9dev/strapi` image instead of building during `docker compose up`.
- Keep `Dockerfile` and package sources in-repo as the image build source for maintainers and image publishing workflows.

## 2026-09-24
- Make `config/database.js` select the database client from `DATABASE_CLIENT` (sqlite default, postgres, mysql) with env-driven connection settings.
- Bundle the `pg` and `mysql2` drivers in the `websoft9dev/strapi` image so external PostgreSQL/MySQL works without a custom build.
- Document the optional external database and its empty-database/data-migration caveat in `.env`, `README.md`, `Notes.md`, and `variables.json`.
