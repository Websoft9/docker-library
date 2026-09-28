#!/usr/bin/env bash
set -uo pipefail

# BASE_URL is provided by `libs app-tests`; no package-specific variables needed.
base="${BASE_URL:?BASE_URL is required}"
# Umami seeds this admin account in the database migration; it is not controlled
# by the package .env, so the smoke test uses the documented default.
user="admin"
password="umami"
deadline=$((SECONDS + 240))

code="000"
while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "${base}/api/heartbeat" || true)
  [ "$code" = "200" ] && break
  sleep 5
done

if [ "$code" != "200" ]; then
  echo "umami heartbeat -> ${code} (timeout)"
  exit 1
fi
echo "umami heartbeat -> 200"

body=$(curl -s --max-time 15 -X POST "${base}/api/auth/login" \
  -H 'Content-Type: application/json' \
  -d "{\"username\":\"${user}\",\"password\":\"${password}\"}" || true)

if printf '%s' "$body" | grep -q '"token"'; then
  echo "umami login ok"
  exit 0
fi

echo "umami login failed: ${body}"
exit 1
