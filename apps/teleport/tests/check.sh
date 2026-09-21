#!/usr/bin/env bash
set -uo pipefail

port="${W9_HTTPS_PORT_SET:-9001}"
base="${BASE_URL:-https://localhost:${port}}"
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 15 "${base}/webapi/ping" || true)
  if [ "$code" = "200" ]; then
    echo "teleport webapi ${base}/webapi/ping -> ${code}"
    exit 0
  fi
  sleep 5
done

echo "teleport webapi ${base}/webapi/ping -> ${code} (timeout)"
exit 1
