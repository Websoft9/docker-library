#!/usr/bin/env bash
set -uo pipefail

port="${W9_HTTPS_PORT_SET:-9443}"
base="${BASE_URL:-https://localhost:${port}}"
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
