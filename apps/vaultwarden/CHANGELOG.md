# CHANGELOG

## 2026-11-25

- Restored the literal host mapping `"9001:80"` so the compose file keeps upstream-style port publishing and stays usable for local self-test. `access` still declares `public: false`, `requireDomain: true`, and `requireHttps: true`, so deployment removes the mapping and serves the vault through an HTTPS gateway only.

## 2026-11-18

- Removed the default plaintext host mapping; access requires an HTTPS gateway.

## 2026-11-17

- Migrated `access` to the V2 port-group array (`vaultwarden:80` with `requireDomain: true`, `requireHttps: true`, and `rootUrl: ["DOMAIN"]`).
- Removed `W9_HTTP_PORT_SET`, `W9_HTTP_PORT`, `W9_URL`, `W9_URL_REPLACE`, and `W9_URL_WITH_PORT`; switched `docker-compose.yml` to literal default port mapping `"9001:80"` and native `DOMAIN` configuration.

## 2026-11-03

- Declared the MariaDB dependency with MySQL/MariaDB external providers and the existing mysql:// DATABASE_URL mapping.
- Recorded MYSQL_* database/account sources and preserved their W9_RCODE password origin; runtime configuration and image versions are unchanged.

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
