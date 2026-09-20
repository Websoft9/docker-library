# CHANGELOG

## 2026-09-11
- Updated PrestaShop from `8.2` to `9.1`.
- Updated the bundled MySQL image from `5.7` (EOL) to `8.4` LTS.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules: braced `${VAR}` references, port purpose comment, template-aligned `.env` layout, and removal of the obsolete `version` and source comments.
- Fixed `PS_DEV_MODE=false` to `PS_DEV_MODE=0` so dev mode is not accidentally enabled by the image entrypoint.
- Added an init script that removes the `install/` folder on container startup, so the back office is no longer blocked by PrestaShop's "delete the /install folder" security check. The upstream image skips its own cleanup because its installer exits non-zero (PrestaShop/docker#465), which aborts the entrypoint before its removal step.
- Added `env.first_startup_only` and `help.db` metadata.
- Expanded `upstream` metadata with the official releases, compose, and documentation sources.
- Regenerated the README.
