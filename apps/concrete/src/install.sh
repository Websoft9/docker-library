#!/bin/bash
# Concrete CMS CLI Installation Script

set -e

echo "=== Concrete CMS Installation Starting ==="

# Wait for MySQL to be ready
echo "Waiting for MySQL to be ready..."
max_attempts=30
attempt=0
while ! mysql -h"$CONCRETE_DB_SERVER" -u"$CONCRETE_DB_USER" -p"$CONCRETE_DB_PASSWORD" -e "SELECT 1" >/dev/null 2>&1; do
  attempt=$((attempt + 1))
  if [ $attempt -ge $max_attempts ]; then
    echo "ERROR: MySQL connection timeout after $max_attempts attempts"
    exit 1
  fi
  echo "Waiting for MySQL ($attempt/$max_attempts)..."
  sleep 2
done

echo "MySQL is ready!"

# Check if Concrete CMS is already installed
if [ -f /var/www/html/application/config/database.php ]; then
  echo "Concrete CMS is already installed. Skipping installation."
  exit 0
fi

# Run Concrete CMS CLI installer
echo "Running c5:install command..."
cd /var/www/html

php concrete/bin/concrete c5:install \
  --db-server="$CONCRETE_DB_SERVER" \
  --db-username="$CONCRETE_DB_USER" \
  --db-password="$CONCRETE_DB_PASSWORD" \
  --db-database="$CONCRETE_DB_NAME" \
  --admin-email="$CONCRETE_ADMIN_EMAIL" \
  --admin-password="$CONCRETE_ADMIN_PASSWORD" \
  --canonical-url="$CONCRETE_CANONICAL_URL" \
  --starting-point="$CONCRETE_STARTING_POINT" \
  --site="Concrete CMS"

# Set proper permissions
chown -R www-data:www-data /var/www/html/application/files
chown -R www-data:www-data /var/www/html/application/config

echo "=== Concrete CMS Installation Complete! ==="
echo "Access your site at: $CONCRETE_CANONICAL_URL"
echo "Admin login: $CONCRETE_ADMIN_EMAIL"
