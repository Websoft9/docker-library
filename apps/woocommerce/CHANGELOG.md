# CHANGELOG

## 2026-11-03

- Declared the MySQL dependency and existing native `WORDPRESS_DB_*` mappings shared by the web and bootstrap services, including external MySQL/MariaDB engines.
- Inherited database names and accounts from the shared dictionary without changing runtime configuration or image versions.

## 2026-09-15

- Added the initial WooCommerce package, based on the official WordPress image with bundled MySQL 8.4.
- Added a `woocommerce-bootstrap` helper that installs and activates the WooCommerce plugin after the first WordPress site install, so the store plugin is enabled by default.
- Added the runtime `W9_URL` override, PHP limits, and gateway tuning (`src/nginx-proxy.conf`) used by the WordPress packages.
- Added a login-page functional check in `tests/cases.yml`.
