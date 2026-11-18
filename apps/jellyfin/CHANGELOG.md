# CHANGELOG

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-30

- Updated Jellyfin from `12.2` to `12.4`.

## 2026-10-13

- Updated Jellyfin from `10.10.7` to `12.2`.
- Upstream renumbered Jellyfin releases from the `10.11.x` line to `12.x`; the first start on `12.x` runs a database/schema migration automatically.
- A full library scan is required after the upgrade to rebuild metadata and refresh library contents.
- Normalized `.env` variable references to the braced `${VAR}` form.

## Release
### Fixes and Enhancements
