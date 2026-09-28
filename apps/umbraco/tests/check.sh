#!/usr/bin/env bash
set -uo pipefail

port="${W9_HTTPS_PORT_SET:-9001}"
base="${BASE_URL:-https://localhost:${port}}"
user="${W9_LOGIN_USER:-admin@example.com}"
password="${W9_LOGIN_PASSWORD:-}"
deadline=$((SECONDS + 300))
code="000"

while [ "$SECONDS" -lt "$deadline" ]; do
  code=$(curl -k -s -o /dev/null -w "%{http_code}" --max-time 15 "${base}/umbraco/" || true)
  case "$code" in
    200|301|302)
      break
      ;;
  esac
  sleep 5
done

if [ "$code" != "200" ] && [ "$code" != "301" ] && [ "$code" != "302" ]; then
  echo "umbraco backoffice ${base}/umbraco/ -> ${code} (timeout)"
  exit 1
fi
echo "umbraco backoffice ${base}/umbraco/ -> ${code}"

if [ -z "$password" ]; then
  echo "W9_LOGIN_PASSWORD is empty; skipping admin login check"
  exit 0
fi

headers_file="$(mktemp)"
body_file="$(mktemp)"
trap 'rm -f "$headers_file" "$body_file"' EXIT

login_code=$(curl -k -s -o "$body_file" -D "$headers_file" -w "%{http_code}" --max-time 15 \
  -X POST "${base}/umbraco/management/api/v1/security/back-office/login" \
  -H 'Content-Type: application/json' \
  --data "{\"username\":\"${user}\",\"password\":\"${password}\"}" || true)

if [ "$login_code" != "200" ]; then
  echo "umbraco admin login -> ${login_code}"
  sed -n '1,80p' "$body_file"
  exit 1
fi

if ! grep -qi '^Set-Cookie: UMB_UCONTEXT=' "$headers_file"; then
  echo "umbraco admin login -> 200 but UMB_UCONTEXT cookie missing"
  sed -n '1,80p' "$headers_file"
  exit 1
fi

echo "umbraco admin login -> ${login_code}"
