# CHANGELOG

## 2026-11-04
- Separated bundled PostgreSQL initialization and health checks from the shared Kong connection inputs.
- Declared external PostgreSQL inputs for Kong and both migration services, preserving default connections and migration ordering.
- Image versions are unchanged; deployment and live migration validation were not performed.

## 2026-11-03
- Declared the internal PostgreSQL dependency and native inputs shared by Kong and both migration services.
- Did not declare external support because bundled database initialization still references application connection inputs; runtime configuration and image versions are unchanged.

## 2026-10-12

- Moved Kong upstream references from `docker-compose.yml` comments into `variables.json > upstream` and refreshed `.env` to the current template layout.
- Corrected `variables.json.access` so the primary browser entry is Kong Manager on port 8002 at `/admin`, while the proxy and Admin API remain documented as separate surfaces.
- Made `kong-migrations-up` use an explicit shell command so `kong migrations finish` is not dropped by YAML/Compose parsing.

## 2026-09-14

- Declared `variables.json.access` for the proxy (`web`, port 8000), admin API (`api`, port 8001), and admin GUI (`admin`, port 8002).
