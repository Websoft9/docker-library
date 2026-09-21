# CHANGELOG

## 2026-09-21

- Update TeamCity to 2026.2 and the bundled MySQL to 8.4.
- Add upstream releases and official docs references to `variables.json`.
- Refresh `.env` to the current template layout; drop the obsolete `-XX:MaxPermSize` JVM flag.
- Normalize `docker-compose.yml` references to `${VAR}`, remove image source comments, and annotate the published port.
- Regenerate `README.md` so the advertised version matches `2026.2` and document first-run setup and agent authorization.
- Add `tests/cases.yml` and `tests/check.sh` covering the TeamCity HTTP endpoint.
- Add `W9_LOGIN_MYSQL_CONNECTION_STRING` so the Websoft9 console shows the MySQL connection string during first-run setup.
