# CHANGELOG

## 2026-10-13

- Updated Gitea from `1.27` to `28.1`; upstream renumbered from the `1.x` line to the new `28.x` scheme and `28.1` is the current stable `x.x` tag.
- Back up the data volume and let Gitea run its automatic database migration on first start; do not roll back the image after the migration.
- Regenerated `README.md` from the updated version metadata.

## 2026-09-13

- Updated Gitea from `1.25` to `1.27`.
- Added `access` metadata for the web UI, admin panel, and API.
- Added `tests/cases.yml` with a health endpoint check that works before the install wizard runs.
- Added repo catalog commercial metadata at `metadata/catalog/gitea.json`.
- Aligned `.env` and `docker-compose.yml` with current repository policy, including braced variable references and inline published-port comments.
- Added a container healthcheck against `/api/healthz`.
- Regenerated `README.md` from `variables.json` and `docker-compose.yml`.
