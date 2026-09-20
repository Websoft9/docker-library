# CHANGELOG

## 2026-09-20

- Updated Vaultwarden from `1.34.3` to `1.37.3`, the latest stable upstream release (includes the 1.35.5 / 1.36.0 / 1.37.0 security fixes).
- Pinned `W9_VERSION` to `1.37.3` and declared it in `variables.json`.
- Bumped the bundled MariaDB dependency from `10.4` (EOL) to `11.4` (LTS).
- Fixed the URL contract by wiring `DOMAIN=https://${W9_URL}`, which the previous `W9_URL_REPLACE=true` declaration lacked (policy gate failure).
- Aligned `.env` and `docker-compose.yml` with current repository policy: braced variable references, inline published-port comment, and the `.env` section banner with a Docs URL.
- Removed the obsolete `version:` key and the `# image:` / `# docs:` source comments.
- Added a healthcheck against `/alive`.
- Added `tests/cases.yml` with an `/alive` check.
- Added upstream releases and documentation references to `variables.json`.
- Regenerated `README.md`.
