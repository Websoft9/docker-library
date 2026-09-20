#!/bin/sh
set -eu

WP="wp --allow-root --path=/var/www/html --require=/usr/local/share/websoft9-url.php"

while [ ! -f /var/www/html/wp-config.php ]; do
  sleep 5
done

until ${WP} core is-installed >/dev/null 2>&1; do
  sleep 10
done

if ! ${WP} plugin is-installed woocommerce >/dev/null 2>&1; then
  ${WP} plugin install woocommerce --version="${WOOCOMMERCE_VERSION}" --activate
else
  ${WP} plugin activate woocommerce >/dev/null 2>&1 || true
fi

${WP} plugin list --format=csv
