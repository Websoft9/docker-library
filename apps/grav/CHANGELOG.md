# CHANGELOG

## 2026-10-15

- Initial package based on the LinuxServer.io `linuxserver/grav` image, pinned to `W9_VERSION=2.2.8` (upstream publishes no `x.x` tag, so the full version tag is intentional).
- Added `docker-compose.yml` with a published web port, the `grav:/config` data volume, and a container healthcheck.
- Added `.env` with image identity, the web port, `W9_URL`, `W9_ADMIN_PATH`, and the LinuxServer.io `PUID`/`PGID`/`TZ` variables.
- Added `variables.json` with upstream references, edition, access ports, and a first-run login note.
- Added `tests/cases.yml` with an admin console reachability check.
- Added the repository catalog entry at `metadata/catalog/grav.json`.
- Added `src/nginx/default.conf`, mounted over `/config/nginx/site-confs/default.conf`, to deny direct web access to Grav's private `tmp/` directory (the Admin2 "user folder exposure" warning).
