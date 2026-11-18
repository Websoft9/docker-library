# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-11-03
- Declared the PostgreSQL dependency, existing native connection inputs, and internal unauthenticated Redis cache.
- Kept the fixed database client, runtime configuration, and image versions unchanged.

## 2026-10-13

- Update Directus from 11.13 to 12.5.0.
- Align `.env` and `docker-compose.yml` with current repository policy and current Directus self-hosting guidance.
- Extend the main container healthcheck window for Directus first-start bootstrap and add app-specific validation coverage for the Directus health endpoint.
