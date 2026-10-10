#!/usr/bin/env bash
set -uo pipefail

port="${W9_DASHBOARD_PORT_SET:-9002}"
base="${BASE_URL:-http://localhost:${port}}"
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 15 "${base}/app/home" || true)
  case "$code" in
    200|301|302)
      break
      ;;
  esac
  sleep 5
done

case "$code" in
  200|301|302)
    echo "opensearch dashboards ${base}/app/home -> ${code}"
    ;;
  *)
    echo "opensearch dashboards ${base}/app/home -> ${code} (timeout)"
    exit 1
    ;;
esac
