# CHANGELOG

## 2026-09-08
- Updated WordPress Pro to `7.1`.
- Updated the bundled MySQL image from `8.0` to `8.4`.
- Changed `W9_ID` to `wordpresspro` so the package no longer collides with the standard WordPress package on the same Docker host.
- Replaced the one-off `init` container URL mutation flow with the same runtime `W9_URL` override approach used by `wordpress`.
- Added an app-local Varnish VCL that passes WordPress admin and authenticated traffic while caching anonymous frontend requests.
- Changed the Varnish backend config from a hard-coded container name to a `${W9_ID}`-derived runtime template.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
