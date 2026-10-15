#!/usr/bin/env bash
# Graylog is reachable in one of two states:
#   - preflight-config: HTTP 401 with `WWW-Authenticate: Basic realm=preflight-config`
#     before the first-time Data Node connection is configured
#   - login page: HTTP 200/302 whose body is the Graylog sign-in page
# Custom cases are not auto-retried by the harness, so poll for startup here.
set -uo pipefail

base="${BASE_URL:?BASE_URL is required}"
body="$(mktemp)"
headers="$(mktemp)"
trap 'rm -f "$body" "$headers"' EXIT

last=""
for _ in $(seq 1 30); do
  code="$(curl -sS -L -D "$headers" -o "$body" -w '%{http_code}' "${base}/" || true)"
  last="$code"
  if [ "$code" = "200" ] || [ "$code" = "302" ]; then
    if grep -Eqi 'graylog|initial configuration|sign in|login' "$body"; then
      echo "Graylog web UI responded with HTTP ${code}"
      exit 0
    fi
  fi
  if [ "$code" = "401" ] && grep -qi 'preflight-config' "$headers"; then
    echo "Graylog web UI is in preflight-config state (HTTP 401)"
    exit 0
  fi
  sleep 5
done

echo "unexpected HTTP ${last} from Graylog web UI" >&2
exit 1
