# CHANGELOG

## 2026-11-17
- Migrated `access` to the V2 port-group array (`wordpress:80` carrying `/` and `/wp-admin`, with `rootUrl` mapped to `WP_HOME` and `WP_SITEURL`).
- Replaced `W9_HTTP_PORT_SET`, `W9_HTTP_PORT`, `W9_URL`, `W9_URL_REPLACE`, and `W9_ADMIN_PATH` with literal default port mapping `"9001:80"` and native `WP_HOME` / `WP_SITEURL` runtime URL overrides in `src/websoft9-url.php`.

## 2026-11-03
- Declared the bundled MySQL dependency and existing native `WORDPRESS_DB_*` mappings for external MySQL/MariaDB connections, inheriting database names and accounts from the shared dictionary.
- Kept runtime configuration and image versions unchanged.

## 2026-10-22
- Checked the WordPress `7.1.3` maintenance and security release. `W9_VERSION=7.1` is already on the same multi-arch digest as `7.1.3`, so no package version change is required.
- Added a `tests/cases.yml` install page check to cover the `/wp-admin/install.php` path.

## 2026-09-15
- Added `src/nginx-proxy.conf` so the Websoft9 Gateway (Nginx Proxy Manager) applies the package upload limit and the platform client rate/concurrency limits for this app.
- The gateway advanced config is consumed platform-side from `src/nginx-proxy.conf`; it is not mounted into any container.

## 2026-09-09
- Declared `W9_URL_REPLACE=true` and passed `W9_URL` / `W9_URL_REPLACE` to the container explicitly so the runtime URL override keeps redirects on the external access address.
- Added a Troubleshooting note clarifying that the first-run `WordPress not found ... copying now` and `wp-config.php` generation logs are normal.
- Regenerated the README.

## 2026-09-08
- Updated WordPress to `7.1`.
- Updated the bundled MySQL image from `8.0` to `8.4`.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
