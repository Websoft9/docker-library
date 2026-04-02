#!/bin/bash
set -e

echo "=== Pimcore Initialization ==="

# Check if Pimcore is already installed
if [ -f /var/www/html/.installed ]; then
    echo "Pimcore already initialized, skipping..."
    exit 0
fi

cd /var/www/html

# Install Pimcore skeleton if composer.json is missing
if [ ! -f /var/www/html/composer.json ]; then
    echo "Creating Pimcore project via composer..."
    composer create-project pimcore/skeleton /tmp/pimcore-install --no-interaction
    cp -rf /tmp/pimcore-install/. /var/www/html/
    rm -rf /tmp/pimcore-install
fi

# Install Pimcore (creates database tables and admin user)
echo "Running pimcore-install..."
php vendor/bin/pimcore-install \
    --admin-username="${W9_LOGIN_USER}" \
    --admin-password="${W9_LOGIN_PASSWORD}" \
    --mysql-host-socket="${PIMCORE_DB_HOST}" \
    --mysql-username="${PIMCORE_DB_USER}" \
    --mysql-password="${PIMCORE_DB_PASSWORD}" \
    --mysql-database="${PIMCORE_DB_NAME}" \
    --no-interaction

# Fix file permissions for web server
chown -R www-data:www-data /var/www/html/var /var/www/html/public 2>/dev/null || echo "Warning: Could not set permissions on var/public directories (non-fatal)"

# Mark as installed to skip on subsequent startups
touch /var/www/html/.installed

echo "=== Pimcore Initialization Complete ==="
