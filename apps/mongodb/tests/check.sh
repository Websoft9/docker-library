#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  result="$(docker exec "${container}" mongosh --quiet --username "${user}" --password "${password}" --authenticationDatabase admin --eval 'db.runCommand({ ping: 1 }).ok' 2>/dev/null || true)"
  if [ "${result}" = "1" ]; then
    echo "MongoDB accepted an authenticated local ping"
    exit 0
  fi
  sleep 5
done

echo "MongoDB did not accept an authenticated ping before timeout" >&2
exit 1
