#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"

response_file="$(mktemp)"
trap 'rm -f "$response_file"' EXIT

status="$(curl -sS -o "$response_file" -w '%{http_code}' \
  "${base}/api/noauth/setup/state")"

if [ "$status" != "200" ]; then
  echo "setup state failed with HTTP ${status}" >&2
  cat "$response_file" >&2
  exit 1
fi

if ! grep -Eq '"status"[[:space:]]*:[[:space:]]*"(ACCOUNT_REQUIRED|READY)"' "$response_file"; then
  echo "unexpected ThingsBoard setup state" >&2
  cat "$response_file" >&2
  exit 1
fi

echo "ThingsBoard first-run setup state is ready"
