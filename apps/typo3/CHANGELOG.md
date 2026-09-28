# CHANGELOG

## 2026-09-21
### Fixes and Enhancements
- Refresh `.env` to the current template layout and add the `TYPO3_*` first-run install variables.
- Normalize `docker-compose.yml` references to `${VAR}`, remove the image source comment, and annotate the published port.
- Regenerate `README.md` so the advertised version matches `13.4`.
- Add `tests/cases.yml` covering the TYPO3 backend login and install tool.
- Add upstream releases and official GitHub/docs references to `variables.json`.
- Pin the bundled MySQL dependency to the `8.4` LTS tag.
- Add non-interactive first-run install via `src/entrypoint.sh`; declare `W9_LOGIN_*` and `W9_URL_REPLACE`.
- Add a healthcheck to the main Typo3 container.
