#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:-http://localhost:${W9_HTTP_PORT_SET:-3000}}"
user="${W9_LOGIN_USER:-admin}"
password="${W9_LOGIN_PASSWORD:-admin}"
jar="$(mktemp)"
trap 'rm -f "$jar"' EXIT

deadline=$((SECONDS + 300))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  page="$(curl -s -c "$jar" --max-time 15 "${base}/login" || true)"
  token="$(printf '%s' "$page" | grep -oE 'name="authenticity_token" value="[^"]+"' | head -1 | sed -E 's/.*value="([^"]+)".*/\1/')"
  if [ -n "${token}" ]; then
    body="$(curl -s -b "$jar" -c "$jar" -L --max-time 15 \
      --data-urlencode "username=${user}" \
      --data-urlencode "password=${password}" \
      --data-urlencode "authenticity_token=${token}" \
      --data-urlencode "login=Login" \
      "${base}/login" || true)"
    if printf '%s' "$body" | grep -q '/logout'; then
      echo "Redmine admin login succeeded"
      exit 0
    fi
  fi
  sleep 5
done

echo "Redmine admin login did not succeed before timeout" >&2
exit 1
