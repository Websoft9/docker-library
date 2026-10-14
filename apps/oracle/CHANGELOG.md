# CHANGELOG

## 2026-10-14

- No new upstream Oracle XE release is available; `container-registry.oracle.com/database/express` still publishes only `21.3.0-xe`, `18.4.0-xe`, and `latest`.
- Refreshed the package for current repository rules: normalized `.env` variable references to `${VAR}`, aligned the `.env` section layout, and documented the Oracle image environment section.
- Removed the obsolete compose `version` key and the legacy `# image:` / `# docs:` source comments, and added inline purpose comments to the published database and EM ports in `docker-compose.yml`.
- Added `tests/cases.yml` with a database listener check, since Oracle XE exposes no HTTP surface on `W9_HTTP_PORT_SET`.
- Regenerated `README.md` from `variables.json`.
