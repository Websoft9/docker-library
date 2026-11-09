#!/bin/sh
set -e

APP_DIR="${APP_DIR:-/var/www/html}"
PUBLIC_DIR="${APP_DIR}/public"
DEFAULT_ICON="/opt/websoft9/favicon.ico"

[ -d "${PUBLIC_DIR}" ] || exit 0
[ -f "${DEFAULT_ICON}" ] || exit 0

# Symfony's error page declares a red-cross favicon. Without a real icon the
# browser keeps requesting /favicon.ico, gets that error page and shows the
# cross in the tab. Only add a default when the app has no icon of its own.
for icon in favicon.ico favicon.svg favicon.png; do
  [ -f "${PUBLIC_DIR}/${icon}" ] && exit 0
done

cp "${DEFAULT_ICON}" "${PUBLIC_DIR}/favicon.ico"
echo "[symfony-runtime] Installed default favicon."
