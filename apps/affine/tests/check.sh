#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

status="$(curl -sS -L -o "$body" -w '%{http_code}' "${base}/")"

case "$status" in
  200) ;;
  *)
    echo "unexpected HTTP ${status} from AFFiNE" >&2
    exit 1
    ;;
esac

if ! grep -Eqi 'AFFiNE|create (your|first) account|workspace' "$body"; then
  echo "response does not look like an AFFiNE landing page" >&2
  exit 1
fi

echo "AFFiNE responded with HTTP ${status}"
