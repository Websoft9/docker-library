# CHANGELOG

## 2026-09-15

- Updated JupyterHub to `6.0`.
- Added the required `jupyterhub upgrade-db` step for JupyterHub 6 startup.
- Moved the persisted hub data directory from the incorrect `/var/www/html` mount to `/srv/jupyterhub`, and made the sqlite database path and cookie secret path explicit in `src/jupyterhub_config.py`.
- Normalized `.env` and `docker-compose.yml` to current repository policy, including braced `${VAR}` references, canonical app defaults, and a port purpose comment.
- Added `variables.json.access`, upstream documentation links, and a first-startup-only note for `W9_LOGIN_PASSWORD`.
- Added a login-page test case and regenerated the README.
