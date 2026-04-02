# src/ - Pimcore Configuration Files

## nginx.conf
Custom Nginx configuration for serving Pimcore. Handles:
- Static asset serving with cache headers
- PHP-FPM proxy to the `php` service on port 9000
- Pimcore-specific rewrite rules (cache-buster, protected assets)
- Static page cache integration

## supervisord.conf
Supervisord configuration for Pimcore background processes:
- `messenger:consume` – processes async jobs (image optimization, maintenance tasks)
- `maintenance` – runs periodic Pimcore maintenance commands

## init.sh
First-run initialization script executed by the `init` container:
1. Installs the Pimcore skeleton project via Composer
2. Runs `pimcore-install` to initialize the database and admin user
3. Creates a `.installed` lock file to skip re-initialization on subsequent startups
