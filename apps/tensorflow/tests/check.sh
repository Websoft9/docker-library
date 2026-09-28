#!/usr/bin/env bash
set -uo pipefail

port="${W9_GUI_PORT_SET:-6006}"
code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "http://localhost:${port}/" || true)

case "$code" in
  200|302)
    echo "tensorboard ui http://localhost:${port}/ -> ${code}"
    exit 0
    ;;
esac

echo "tensorboard ui http://localhost:${port}/ -> ${code}"
exit 1
