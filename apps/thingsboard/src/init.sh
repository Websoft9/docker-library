#!/usr/bin/env bash
set -euo pipefail

if [[ ! -f /data/.tb-installed ]]; then
    if ! mkdir /data/.tb-installing; then
        echo "Installation is unfinished or /data is not writable; review logs before retrying" >&2
        exit 1
    fi
    echo "Installing ThingsBoard"
    unset LOAD_DEMO
    INSTALL_TB=true UPGRADE_TB=false /usr/bin/start-tb-node.sh
    touch /data/.tb-installed
    rmdir /data/.tb-installing
fi

unset INSTALL_TB LOAD_DEMO UPGRADE_TB
exec /usr/bin/start-tb-node.sh