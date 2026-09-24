#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"
query="SELECT @@VERSION;"
tool=""

for candidate in /opt/mssql-tools18/bin/sqlcmd /opt/mssql-tools/bin/sqlcmd; do
  if docker exec "${container}" test -x "${candidate}" >/dev/null 2>&1; then
    tool="${candidate}"
    break
  fi
done

if [ -z "${tool}" ]; then
  echo "sqlcmd not found in ${container}" >&2
  exit 1
fi

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  if docker exec "${container}" "${tool}" -S localhost -U "${user}" -P "${password}" -Q "${query}" -C >/dev/null 2>&1 || \
     docker exec "${container}" "${tool}" -S localhost -U "${user}" -P "${password}" -Q "${query}" >/dev/null 2>&1; then
    echo "SQL Server accepted a local sqlcmd query"
    exit 0
  fi
  sleep 5
done

echo "sqlcmd query did not succeed before timeout" >&2
exit 1
