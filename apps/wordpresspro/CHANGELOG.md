# CHANGELOG

## 2026-09-15
- Added a bundled Redis `7.4` service for WordPress object caching.
- Extended `src/websoft9-url.php` so the package injects `WP_REDIS_*` constants and `WP_CACHE` at runtime from `.env`, matching the existing runtime URL override approach.
- Added a `redis-bootstrap` helper service that waits for the first WordPress site install, then installs and activates the `Redis Object Cache` plugin and runs `wp redis enable` automatically.
- Passed Redis connection settings through `.env` and updated package metadata for the new bundled Redis dependency.
- Raised the recommended memory floor to `2 GB`, added `variables.json.access`, and added a functional test case for the install page.
- Simplified Redis to internal unauthenticated access on the app network; WordPress no longer passes a Redis password for this package.
- Tightened the Varnish VCL so it explicitly caches static assets, bypasses WooCommerce and other stateful paths, and avoids caching dynamic query-string requests.
- Added `src/nginx-proxy.conf` so the Websoft9 Gateway (Nginx Proxy Manager) applies the package upload limit and the platform client rate/concurrency limits for this app.

## 2026-09-09
- Declared `W9_URL_REPLACE=true` and passed `W9_URL` / `W9_URL_REPLACE` to the container explicitly so the runtime URL override keeps redirects on the external access address.
- Added a Troubleshooting note clarifying that the first-run `WordPress not found ... copying now` and `wp-config.php` generation logs are normal.
- Regenerated the README.

## 2026-09-08
- Updated WordPress Pro to `7.1`.
- Updated the bundled MySQL image from `8.0` to `8.4`.
- Changed `W9_ID` to `wordpresspro` so the package no longer collides with the standard WordPress package on the same Docker host.
- Replaced the one-off `init` container URL mutation flow with the same runtime `W9_URL` override approach used by `wordpress`.
- Added an app-local Varnish VCL that passes WordPress admin and authenticated traffic while caching anonymous frontend requests.
- Changed the Varnish backend config from a hard-coded container name to a `${W9_ID}`-derived runtime template.
- Normalized `.env` and `docker-compose.yml` to current repository policy rules.
- Regenerated the README.
