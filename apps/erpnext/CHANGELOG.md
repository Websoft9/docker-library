# CHANGELOG

## 2026-11-05

- Replaced the unavailable `mysqladmin` probe with the MariaDB image's `healthcheck.sh --connect --innodb_initialized`.
- Verified fresh deployment, retained-volume recreation, administrator login, and database-marker preservation across the database-declaration baseline-to-current configuration change on the remote test server.
- Kept image versions and database volumes unchanged; this was not a database major-version upgrade. Owner E2E remains pending.

## 2026-11-04

- Declared internal MariaDB and the two distinct Redis cache/queue instances, retaining their unauthenticated configuration.
- Recorded only the known root initialization/administration account from MYSQL_ROOT_PASSWORD; did not guess dynamically generated site databases or business users.
- Kept the complex bundled stack internal-only and removed the external provider, mapping, and external-only DB_HOST/DB_PORT/DB_PASSWORD inputs.
- Restored the bundled database address; kept the independent fix using W9_POWER_PASSWORD for the provisioning root account and W9_LOGIN_PASSWORD for the application administrator.
- Verified fresh/existing-site behavior with command substitutes; declarations do not rewrite saved site credentials or migrate data. No deployment, live connection, or image upgrade was performed.

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
