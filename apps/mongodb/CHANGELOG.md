# CHANGELOG

## 2026-09-30

- Prune MongoDB versions that are out of vendor maintenance, keeping only the maintained tracks `8.3`, `8.0`, and `7.0` (plus `latest`).
- Move the default image to `7.0`: the maintained `8.3` and `8.0` images still refuse to start on Linux kernel 6.19+/Ubuntu 26.04 (upstream fix pending in 8.3.14 / 8.0.35).
- Track MongoDB lifecycle facts in `metadata/db-lifecycle.json`.
- Normalize the package to current conventions: braced `${VAR}` references, documented port purpose, inline `command`, and refreshed upstream metadata.
- Record first-startup-only credential variables and add a mongosh connectivity smoke test for deployment validation.
