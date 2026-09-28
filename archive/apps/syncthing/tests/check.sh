#!/usr/bin/env bash
set -euo pipefail

deadline=$((SECONDS + 120))
config_file="/var/syncthing/config/config.xml"
status="pending"

while [ "$SECONDS" -lt "$deadline" ]; do
  if docker exec syncthing sh -c "grep -q '<user>${W9_LOGIN_USER}</user>' ${config_file} && grep -q '<password>\\$2' ${config_file}" >/dev/null 2>&1; then
    status="ok"
    break
  fi
  sleep 3
done

if [ "${status}" != "ok" ]; then
  echo "Syncthing GUI credentials were not written to ${config_file} during first startup" >&2
  exit 1
fi

echo "Syncthing GUI credentials were written to ${config_file} on first startup"
