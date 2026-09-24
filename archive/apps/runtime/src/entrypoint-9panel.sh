#!/bin/sh
# vim:sw=4:ts=4:et

set -e

sed -i "s/var set_infrastructure=.*/var set_infrastructure=\"$RUNTIME_LANG\"/g" /usr/share/nginx/html/js/websoft9.js