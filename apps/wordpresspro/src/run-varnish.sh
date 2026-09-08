#!/bin/sh
set -eu

backend_host="${W9_ID}-wordpress"
sed "s/__WORDPRESS_BACKEND__/${backend_host}/g" /etc/varnish/default.vcl.template > /tmp/default.vcl

exec varnishd -F -f /tmp/default.vcl -s "malloc,${VARNISH_SIZE}"
