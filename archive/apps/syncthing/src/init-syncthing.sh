#!/bin/sh

set -eu

CONFIG_DIR="${STHOMEDIR:-/var/syncthing/config}"
DATA_DIR="${HOME:-/var/syncthing}"
CONFIG_FILE="${CONFIG_DIR}/config.xml"

fix_ownership() {
    if [ "$(id -u)" = "0" ]; then
        chown -R "${PUID:-1000}:${PGID:-1000}" "${DATA_DIR}" || true
    fi
}

if [ ! -f "${CONFIG_FILE}" ] && [ -n "${W9_LOGIN_USER:-}" ] && [ -n "${W9_LOGIN_PASSWORD:-}" ]; then
    mkdir -p "${CONFIG_DIR}"
    syncthing generate \
        --home="${CONFIG_DIR}" \
        --gui-user="${W9_LOGIN_USER}" \
        --gui-password="${W9_LOGIN_PASSWORD}" \
        --no-port-probing >/dev/null
fi

fix_ownership

exec /bin/entrypoint.sh /bin/syncthing
