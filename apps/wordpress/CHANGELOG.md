# CHANGELOG

## 2026-09-09
- Declared `W9_URL_REPLACE=true` and passed `W9_URL` / `W9_URL_REPLACE` to the container explicitly so the runtime URL override keeps redirects on the external access address.
- Added a Troubleshooting note clarifying that the first-run `WordPress not found ... copying now` and `wp-config.php` generation logs are normal.
- Regenerated the README.

## 2026-09-08
- Updated WordPress to `7.1`.
- Updated the bundled MySQL image from `8.0` to `8.4`.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
