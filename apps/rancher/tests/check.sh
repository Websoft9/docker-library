#!/usr/bin/env bash
set -uo pipefail

base="${BASE_URL:-https://localhost:9004}"
deadline=$((SECONDS + 300))
code="000"

while [ "${SECONDS}" -lt "${deadline}" ]; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 20 "${base}/" || true)
  case "${code}" in
    200|301|302|303) break ;;
  esac
  sleep 5
done

if [ "${code}" != "200" ] && [ "${code}" != "301" ] && [ "${code}" != "302" ] && [ "${code}" != "303" ]; then
  echo "rancher ${base}/ -> ${code} (timeout)"
  exit 1
fi
echo "rancher ${base}/ -> ${code}"
