#!/bin/bash
set -e

TYPO3_CLI="/var/www/html/typo3/sysext/core/bin/typo3"
SETTINGS_FILE="/var/www/html/typo3conf/system/settings.php"
FIRST_INSTALL_FILE="/var/www/html/FIRST_INSTALL"
DB_HOST="${TYPO3_DB_HOST:-localhost}"
DB_PORT="${TYPO3_DB_PORT:-3306}"
MAX_RETRIES="${TYPO3_SETUP_MAX_RETRIES:-60}"
RETRY_INTERVAL="${TYPO3_SETUP_RETRY_INTERVAL:-5}"

if [ -n "${TYPO3_SETUP_ADMIN_PASSWORD:-}" ] && [ ! -f "$SETTINGS_FILE" ]; then
    echo "websoft9: waiting for database at ${DB_HOST}:${DB_PORT} ..."
    retries=0
    until php -r "@\$sock = fsockopen('${DB_HOST}', (int)'${DB_PORT}', \$errno, \$errstr, 1); if (!\$sock) { exit(1); } fclose(\$sock);" >/dev/null 2>&1; do
        retries=$((retries + 1))
        if [ "$retries" -ge "$MAX_RETRIES" ]; then
            echo "websoft9: database not reachable after $((MAX_RETRIES * RETRY_INTERVAL))s; leaving the browser install tool in place."
            break
        fi
        sleep "$RETRY_INTERVAL"
    done

    if [ "$retries" -lt "$MAX_RETRIES" ]; then
        echo "websoft9: running non-interactive TYPO3 setup ..."
        runuser -u www-data -- "$TYPO3_CLI" setup --force --no-interaction --server-type="${TYPO3_SERVER_TYPE:-apache}"
        rm -f "$FIRST_INSTALL_FILE"
        echo "websoft9: TYPO3 setup complete."
    fi
fi

if [ "$#" -eq 0 ]; then
    set -- apache2-foreground
fi

exec docker-php-entrypoint "$@"
