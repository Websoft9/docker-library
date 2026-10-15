# CHANGELOG

## 2026-10-14

- Updated MLflow from `v3.1.4` to `v3.17.1`, the latest stable upstream release.
- Aligned `.env` with the current repository layout, normalized variable references, and documented the MLflow server environment section.
- Set `MLFLOW_SERVER_ALLOWED_HOSTS=*` so the MLflow 3.x DNS-rebinding protection does not reject access through the public host or IP.
- Removed the dead `build` named volume that over-mounted the image's bundled frontend assets, and dropped the obsolete compose `version` key.
- Added `tests/cases.yml` with a `/health` reachability check.
- Added upstream releases, compose, and docs references to `variables.json`.
- Regenerated `README.md` from `variables.json`.

## 2024-12-27

- First release.
