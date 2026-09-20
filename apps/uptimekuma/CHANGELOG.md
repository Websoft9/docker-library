# CHANGELOG

## 2026-09-20

- Updated `W9_VERSION` from `2.0.2` to `2.5.5` and aligned `variables.json.edition` with the current upstream tag (upstream publishes no `x.x` tag, so the patch pin is intentional).
- Normalized `.env` and `docker-compose.yml` to current repository policy: braced `${VAR}` references, a port purpose comment, no image/docs source comments, and no obsolete compose `version` key.
- Added `upstream.releases`, `upstream.docs`, and `variables.json.access`.
- Added `tests/cases.yml` with an entry-page API check.
- Regenerated `README.md` from `variables.json` and `docker-compose.yml`.
