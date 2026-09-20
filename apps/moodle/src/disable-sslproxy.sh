#!/bin/bash
# The elestio image enables $CFG->sslproxy because Elestio terminates TLS in
# front of it. This package serves plain HTTP (W9_HTTP_PORT_SET), so a forced
# SSL proxy makes Moodle redirect to HTTPS and fail. Remove it after install.
CONFIG=/var/www/html/config.php

if [ -f "$CONFIG" ] && grep -q 'sslproxy' "$CONFIG"; then
  sed -i '/sslproxy/d' "$CONFIG"
  echo "[w9] removed \$CFG->sslproxy from config.php"
fi
