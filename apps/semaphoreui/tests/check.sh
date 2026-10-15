#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:-http://localhost:3000}"
user="${W9_LOGIN_USER:-admin}"
password="${W9_LOGIN_PASSWORD:-changeme}"

deadline=$((SECONDS + 300))
status=""
while [ "${SECONDS}" -lt "${deadline}" ]; do
  status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 \
    -H 'Content-Type: application/json' \
    --data "{\"auth\":\"${user}\",\"password\":\"${password}\"}" \
    "${base}/api/auth/login" || true)"
  if [ "${status}" = "204" ]; then
    echo "Semaphore UI admin login succeeded"
    exit 0
  fi
  sleep 5
done

echo "Semaphore UI admin login did not succeed before timeout (last status ${status:-none})" >&2
exit 1
