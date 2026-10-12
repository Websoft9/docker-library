#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  result="$(docker exec "${container}" redis-cli --no-auth-warning -a "${password}" ping 2>/dev/null || true)"
  if [ "${result}" = "PONG" ]; then
    echo "Redis accepted an authenticated local ping"
    exit 0
  fi
  sleep 5
done

echo "Redis did not accept an authenticated ping before timeout" >&2
exit 1
