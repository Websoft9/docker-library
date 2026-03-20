#!/bin/bash
set -euo pipefail

: "${MOODLE_DB_HOST:=}"
: "${MOODLE_DB_PORT:=3306}"
: "${MOODLE_DB_NAME:=moodle}"
: "${MOODLE_DB_USER:=moodle}"
: "${MOODLE_DB_PASSWORD:=}"
: "${MOODLE_DB_TYPE:=mariadb}"
: "${MOODLE_DATA:=/var/moodledata}"
: "${MOODLE_URL:=http://localhost}"
: "${MOODLE_ADMIN_USER:=admin}"
: "${MOODLE_ADMIN_PASSWORD:=${MOODLE_DB_PASSWORD}}"
: "${MOODLE_ADMIN_EMAIL:=admin@example.com}"
: "${MOODLE_SITE_NAME:=Moodle Learning Platform}"

# Start cron daemon (runs in background, handles /etc/crontab)
# Remove stale pid file that persists across container restarts (writable layer is preserved),
# which would cause cron to refuse to start and exit non-zero, triggering set -e.
rm -f /var/run/cron.pid 2>/dev/null || true
cron

# Restore config.php from moodledata if it was persisted after a previous install
if [ -f "${MOODLE_DATA}/.moodle_config.php" ] && [ ! -f /var/www/html/config.php ]; then
    echo "Restoring config.php from moodledata..."
    cp "${MOODLE_DATA}/.moodle_config.php" /var/www/html/config.php
fi

# Wait for the database to be ready (max 120 seconds)
if [ -n "${MOODLE_DB_HOST}" ]; then
    echo "Waiting for database at ${MOODLE_DB_HOST}:${MOODLE_DB_PORT}..."
    timeout=120
    elapsed=0
    until mysqladmin ping \
            -h "${MOODLE_DB_HOST}" \
            -P "${MOODLE_DB_PORT}" \
            -u "${MOODLE_DB_USER}" \
            -p"${MOODLE_DB_PASSWORD}" \
            --silent 2>/dev/null; do
        if [ "${elapsed}" -ge "${timeout}" ]; then
            echo "ERROR: Database did not become ready within ${timeout}s" >&2
            exit 1
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done
    echo "Database is ready."
fi

# Install or upgrade Moodle
if [ ! -f /var/www/html/config.php ]; then
    echo "Starting Moodle installation..."
    php /var/www/html/admin/cli/install.php \
        --lang=en \
        --wwwroot="${MOODLE_URL}" \
        --dataroot="${MOODLE_DATA}" \
        --dbtype="${MOODLE_DB_TYPE}" \
        --dbhost="${MOODLE_DB_HOST}" \
        --dbname="${MOODLE_DB_NAME}" \
        --dbuser="${MOODLE_DB_USER}" \
        --dbpass="${MOODLE_DB_PASSWORD}" \
        --dbport="${MOODLE_DB_PORT}" \
        --prefix=mdl_ \
        --fullname="${MOODLE_SITE_NAME}" \
        --shortname="Moodle" \
        --adminuser="${MOODLE_ADMIN_USER}" \
        --adminpass="${MOODLE_ADMIN_PASSWORD}" \
        --adminemail="${MOODLE_ADMIN_EMAIL}" \
        --non-interactive \
        --agree-license
    echo "Moodle installation complete."
    # Persist config.php to moodledata so it survives container recreations
    cp /var/www/html/config.php "${MOODLE_DATA}/.moodle_config.php"
elif php /var/www/html/admin/cli/upgrade.php --is-pending --non-interactive 2>/dev/null | grep -q "pending\|Upgrade"; then
    echo "Database upgrade pending, running upgrade..."
    php /var/www/html/admin/cli/upgrade.php --non-interactive
    echo "Moodle upgrade complete."
    cp /var/www/html/config.php "${MOODLE_DATA}/.moodle_config.php"
fi

# Ensure correct permissions
chown -R www-data:www-data /var/www/html
chown -R www-data:www-data "${MOODLE_DATA}"

exec "$@"
