#!/bin/bash
set -e

# Start cron service
service cron start

# Wait for database to be ready
if [ -n "$MOODLE_DB_HOST" ]; then
    echo "Waiting for database to be ready..."
    for i in {1..30}; do
        if mysqladmin ping -h"$MOODLE_DB_HOST" -u"${MOODLE_DB_USER:-moodle}" -p"${MOODLE_DB_PASSWORD}" --silent 2>/dev/null; then
            echo "Database is ready!"
            break
        fi
        echo "Waiting for database... ($i/30)"
        sleep 2
    done
fi

# If config.php doesn't exist, create it from environment variables
if [ ! -f /var/www/html/config.php ] && [ -n "$MOODLE_DB_HOST" ]; then
    cat > /var/www/html/config.php <<EOF
<?php  // Moodle configuration file

unset(\$CFG);
global \$CFG;
\$CFG = new stdClass();

\$CFG->dbtype    = '${MOODLE_DB_TYPE:-mariadb}';
\$CFG->dblibrary = 'native';
\$CFG->dbhost    = '${MOODLE_DB_HOST}';
\$CFG->dbname    = '${MOODLE_DB_NAME:-moodle}';
\$CFG->dbuser    = '${MOODLE_DB_USER:-moodle}';
\$CFG->dbpass    = '${MOODLE_DB_PASSWORD}';
\$CFG->prefix    = 'mdl_';
\$CFG->dboptions = array(
    'dbpersist' => 0,
    'dbport' => '${MOODLE_DB_PORT:-3306}',
    'dbsocket' => '',
    'dbcollation' => 'utf8mb4_unicode_ci',
);

\$CFG->wwwroot   = '${MOODLE_URL:-http://localhost}';
\$CFG->dataroot  = '${MOODLE_DATA:-/var/moodledata}';
\$CFG->admin     = 'admin';

\$CFG->directorypermissions = 0777;

require_once(__DIR__ . '/lib/setup.php');

// There is no php closing tag in this file,
// it is intentional because it prevents trailing whitespace problems!
EOF

    chown www-data:www-data /var/www/html/config.php
    chmod 0644 /var/www/html/config.php

    # Run installation if MOODLE_ADMIN_USER is set
    if [ -n "$MOODLE_ADMIN_USER" ]; then
        echo "Installing Moodle..."
        php /var/www/html/admin/cli/install.php \
            --lang=en \
            --wwwroot="${MOODLE_URL:-http://localhost}" \
            --dataroot="${MOODLE_DATA:-/var/moodledata}" \
            --dbtype="${MOODLE_DB_TYPE:-mysqli}" \
            --dbhost="${MOODLE_DB_HOST}" \
            --dbname="${MOODLE_DB_NAME:-moodle}" \
            --dbuser="${MOODLE_DB_USER:-moodle}" \
            --dbpass="${MOODLE_DB_PASSWORD}" \
            --dbport="${MOODLE_DB_PORT:-3306}" \
            --prefix=mdl_ \
            --fullname="${MOODLE_SITE_NAME:-Moodle Site}" \
            --shortname="${MOODLE_SITE_SHORT:-Moodle}" \
            --adminuser="${MOODLE_ADMIN_USER:-admin}" \
            --adminpass="${MOODLE_ADMIN_PASSWORD}" \
            --adminemail="${MOODLE_ADMIN_EMAIL:-admin@example.com}" \
            --non-interactive \
            --agree-license || echo "Installation may already be completed"
    fi
fi

# Fix permissions
chown -R www-data:www-data /var/www/html
chown -R www-data:www-data ${MOODLE_DATA:-/var/moodledata}

# Execute the CMD
exec "$@"
