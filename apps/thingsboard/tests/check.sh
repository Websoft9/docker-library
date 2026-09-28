#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
user="${W9_LOGIN_USER:?W9_LOGIN_USER is required}"
password="${W9_LOGIN_PASSWORD:?W9_LOGIN_PASSWORD is required}"

response_file="$(mktemp)"
trap 'rm -f "$response_file"' EXIT

status="$(curl -sS -o "$response_file" -w '%{http_code}' \
  -X POST "${base}/api/auth/login" \
  -H 'Content-Type: application/json' \
  --data "{\"username\":\"${user}\",\"password\":\"${password}\"}")"

if [ "$status" != "200" ]; then
  echo "login failed with HTTP ${status}" >&2
  cat "$response_file" >&2
  exit 1
fi

if ! grep -q '"token"' "$response_file"; then
  echo "login response has no token" >&2
  cat "$response_file" >&2
  exit 1
fi

echo "ThingsBoard API login succeeded"
