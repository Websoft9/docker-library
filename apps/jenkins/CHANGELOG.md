# CHANGELOG

## 2026-11-26

- Added `help.init` and `help.login` describing the `initialAdminPassword` file and the unlock/setup flow.

## 2026-11-17

- Migrated `access` to the V2 port-group array and removed deprecated `W9_*` port/URL aliases in `.env` and `docker-compose.yml`.

## 2026-10-27
- Updated Jenkins from `2.586` to `2.587`.
- Regenerated the README.

## 2026-10-13
- Updated Jenkins from `2.581` to `2.586`.
- Regenerated the README.

## 2026-09-12
- Updated Jenkins from `2.540` to `2.581`.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules (braced `${VAR}` references, port purpose comment, removal of the obsolete `version` and source comments).
- Expanded `upstream` metadata with the official release and documentation sources.
- Declared `variables.json.credentials.password` as a `container-file` source for Jenkins' generated initial admin password.
- Regenerated the README.
