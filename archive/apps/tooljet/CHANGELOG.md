# CHANGELOG

## 2026-09-15

- Updated ToolJet to `v3.20.226-lts` (upstream has no `x.x` tag; the `v3.21.x` line is prerelease only).
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image/docs source comments, and no obsolete compose `version` key.
- Bundled PostgreSQL is now driven by `W9_DB_VERSION`; pinned the postgrest dependency from `latest` to `v12.0.2` and moved its `PGRST_*` connection settings into `.env`.
- Renamed `src/nginx_proxy.conf` to `src/nginx-proxy.conf`, the name the Websoft9 platform actually reads.
- Fixed the `trademark` typo, declared `variables.json.access`, and added upstream documentation links.
- Added a login-page functional check in `tests/cases.yml` and regenerated the README.
- Added a short ToolJet MCP setup note to the README.


