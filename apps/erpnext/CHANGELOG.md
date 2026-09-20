# CHANGELOG

## 2026-09-14

- Updated ERPNext to the `v16` release line and kept `v16.34.2` in `variables.json.edition` as the assessed upstream version reference.
- Updated the bundled MariaDB dependency from the EOL `10.6` to the upstream-tested `11.8` LTS, and dropped the MariaDB 10.6-only `--skip-innodb-read-only-compressed` flag.
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, and no image/docs source comments.
- Declared `variables.json.access`, added `upstream.docs`, and added first-startup-only notes for the admin and DB credentials.
- Added a login-page check in `tests/cases.yml`.
- Regenerated the README.

## 2026-03-12

- Upgraded ERPNext to v16.
- Added the HR module introduced in ERPNext v16.
