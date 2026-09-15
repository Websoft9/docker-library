#!/bin/sh
set -eu

WP="wp --allow-root --path=/var/www/html --require=/usr/local/share/websoft9-url.php"

while [ ! -f /var/www/html/wp-config.php ]; do
  sleep 5
done

until php -r '$host = getenv("WP_REDIS_HOST"); $port = (int) getenv("WP_REDIS_PORT"); $socket = @fsockopen($host, $port, $errno, $errstr, 2); if ($socket) { fclose($socket); exit(0); } exit(1);'; do
  sleep 5
done

until ${WP} core is-installed >/dev/null 2>&1; do
  sleep 10
done

if ! ${WP} plugin is-installed redis-cache >/dev/null 2>&1; then
  ${WP} plugin install redis-cache --activate
else
  ${WP} plugin activate redis-cache >/dev/null 2>&1 || true
fi

${WP} redis enable || true

${WP} redis status
