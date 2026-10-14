#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  if docker exec "${container}" curl -fsS -u "${user}:${password}" "http://127.0.0.1:5984/" >/dev/null 2>&1; then
    echo "CouchDB accepted an authenticated local API request"
    exit 0
  fi
  sleep 5
done

echo "CouchDB did not accept an authenticated API request before timeout" >&2
exit 1
