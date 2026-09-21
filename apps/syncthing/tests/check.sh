#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
deadline=$((SECONDS + 120))
status="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  status="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 "${base}/rest/system/config" || true)"
  [ "${status}" != "000" ] && break
  sleep 3
done

if [ "${status}" != "403" ]; then
  echo "expected anonymous GUI API access to be blocked with HTTP 403, got ${status}" >&2
  exit 1
fi

echo "Syncthing GUI API blocks anonymous access as expected"
