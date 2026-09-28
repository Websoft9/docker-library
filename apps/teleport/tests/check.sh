#!/usr/bin/env bash
set -uo pipefail

port="${W9_HTTPS_PORT_SET:-9001}"
base="${BASE_URL:-https://localhost:${port}}"
user="${W9_LOGIN_USER:-admin}"
password="${W9_LOGIN_PASSWORD:-}"
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 15 "${base}/webapi/ping" || true)
  if [ "$code" = "200" ]; then
    break
  fi
  sleep 5
done

if [ "$code" != "200" ]; then
  echo "teleport webapi ${base}/webapi/ping -> ${code} (timeout)"
  exit 1
fi
echo "teleport webapi ${base}/webapi/ping -> ${code}"

if [ -z "$password" ]; then
  echo "W9_LOGIN_PASSWORD is empty; skipping admin login check"
  exit 0
fi

login_code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 15 \
  -X POST "${base}/webapi/sessions/web" \
  -H 'Content-Type: application/json' \
  --data "{\"user\":\"${user}\",\"pass\":\"${password}\",\"second_factor_token\":\"\"}" || true)

if [ "$login_code" != "200" ]; then
  echo "teleport admin login -> ${login_code}"
  exit 1
fi
echo "teleport admin login -> ${login_code}"
