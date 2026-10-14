#!/usr/bin/env bash
set -euo pipefail

base_url="${BASE_URL%/}"

login_page_status="$(curl -k -sS -o /dev/null -w "%{http_code}" "${base_url}/login")"
if [ "${login_page_status}" != "200" ]; then
  echo "expected /login to return 200, got ${login_page_status}"
  exit 1
fi

session_headers="$(mktemp)"
session_body="$(mktemp)"
trap 'rm -f "${session_headers}" "${session_body}"' EXIT

login_status="$(curl -k -sS -o "${session_body}" -w "%{http_code}" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -D "${session_headers}" \
  --data-urlencode "password=${W9_POWER_PASSWORD}" \
  --data-urlencode "base=." \
  --data-urlencode "href=${base_url}/" \
  "${base_url}/login")"

if [ "${login_status}" != "302" ]; then
  echo "expected login POST to return 302, got ${login_status}"
  cat "${session_headers}"
  cat "${session_body}"
  exit 1
fi

if ! grep -qi '^set-cookie: code-server-session=' "${session_headers}"; then
  echo "missing code-server-session cookie after successful login"
  cat "${session_headers}"
  exit 1
fi
