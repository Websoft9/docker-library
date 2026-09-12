# CHANGELOG

## 2026-09-12
- Updated Jenkins from `2.540` to `2.581`.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules (braced `${VAR}` references, port purpose comment, removal of the obsolete `version` and source comments).
- Expanded `upstream` metadata with the official release and documentation sources.
- Declared `variables.json.credentials.password` as a `container-file` source for Jenkins' generated initial admin password.
- Regenerated the README.
