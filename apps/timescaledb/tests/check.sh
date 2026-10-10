#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"
db="${W9_ID:?W9_ID is required}"

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  result="$(docker exec -e PGPASSWORD="${password}" "${container}" psql -U "${user}" -d "${db}" -tAc "SELECT extname FROM pg_extension WHERE extname = 'timescaledb';" 2>/dev/null | tr -d '[:space:]' || true)"
  if [ "${result}" = "timescaledb" ]; then
    echo "TimescaleDB extension is available in the default database"
    exit 0
  fi
  sleep 5
done

echo "TimescaleDB extension was not detected before timeout" >&2
exit 1
