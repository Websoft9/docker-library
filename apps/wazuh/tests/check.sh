#!/usr/bin/env bash
set -uo pipefail

base="${BASE_URL:-https://localhost:9443}"
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 15 "${base}/" || true)
  case "$code" in
    200|301|302)
      echo "wazuh dashboard ${base}/ -> ${code}"
      exit 0
      ;;
  esac
  sleep 5
done

echo "wazuh dashboard ${base}/ -> ${code} (timeout)"
exit 1
