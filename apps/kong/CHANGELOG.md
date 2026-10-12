# CHANGELOG

## 2026-10-12

- Moved Kong upstream references from `docker-compose.yml` comments into `variables.json > upstream` and refreshed `.env` to the current template layout.
- Corrected `variables.json.access` so the primary browser entry is Kong Manager on port 8002 at `/admin`, while the proxy and Admin API remain documented as separate surfaces.
- Made `kong-migrations-up` use an explicit shell command so `kong migrations finish` is not dropped by YAML/Compose parsing.

## 2026-09-14

- Declared `variables.json.access` for the proxy (`web`, port 8000), admin API (`api`, port 8001), and admin GUI (`admin`, port 8002).
