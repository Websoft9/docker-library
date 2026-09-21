#!/usr/bin/env bash
set -uo pipefail

# BASE_URL is provided by `libs app-tests`; no package-specific variables needed.
base="${BASE_URL:?BASE_URL is required}"
body_file="$(mktemp)"
trap 'rm -f "$body_file"' EXIT
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -s -L -o "$body_file" -w "%{http_code}" --max-time 20 "${base}/" || true)
  if [ "$code" = "200" ] && grep -qi "xwiki" "$body_file"; then
    echo "xwiki webapp served at ${base}/ (200)"
    exit 0
  fi
  sleep 5
done

echo "xwiki webapp -> ${code} (timeout)"
exit 1
