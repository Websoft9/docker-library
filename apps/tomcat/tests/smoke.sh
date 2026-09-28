#!/usr/bin/env bash
set -euo pipefail

# BASE_URL is provided by `libs app-tests`.
base="${BASE_URL:?BASE_URL is required}"
body="$(curl -fsS --max-time 15 "${base}/")"

if printf '%s' "${body}" | grep -qi "tomcat"; then
  echo "tomcat welcome page served at ${base}/"
  exit 0
fi

echo "unexpected response from ${base}/" >&2
exit 1
