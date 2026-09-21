# CHANGELOG

## 2026-09-21
### Fixes and Enhancements
- Update ThingsBoard to 4.3.1 and the bundled PostgreSQL to 18.
- Correct `variables.json` upstream image from `thingsboard/tb-postgres` to `thingsboard/tb-node`; add releases and official docs references.
- Refresh `.env` to the current template layout and add `W9_DB_VERSION`.
- Normalize `docker-compose.yml` references to `${VAR}`, remove image source comments, and annotate the published port.
- Regenerate `README.md` so the advertised version matches `4.3.1`.
- Add `tests/cases.yml` and `tests/check.sh` covering the ThingsBoard REST login.
