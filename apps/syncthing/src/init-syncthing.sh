#!/bin/sh

set -eu

CONFIG_DIR="${STHOMEDIR:-/var/syncthing/config}"
CONFIG_FILE="${CONFIG_DIR}/config.xml"

if [ ! -f "${CONFIG_FILE}" ] && [ -n "${W9_LOGIN_USER:-}" ] && [ -n "${W9_LOGIN_PASSWORD:-}" ]; then
    mkdir -p "${CONFIG_DIR}"
    syncthing generate \
        --home="${CONFIG_DIR}" \
        --gui-user="${W9_LOGIN_USER}" \
        --gui-password="${W9_LOGIN_PASSWORD}" \
        --no-port-probing >/dev/null
fi

exec /bin/entrypoint.sh /bin/syncthing
