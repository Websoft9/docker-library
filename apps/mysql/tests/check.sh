#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
login_secret="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  result="$(docker exec --env "MYSQL_PWD=${login_secret}" "${container}" mysql --user="${user}" --batch --skip-column-names --execute='SELECT 1' 2>/dev/null || true)"
  if [ "${result}" = "1" ]; then
    echo "MySQL accepted an authenticated SQL query"
    exit 0
  fi
  sleep 5
done

echo "MySQL did not accept an authenticated SQL query before timeout" >&2
exit 1
