#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

code="$(curl -sS -o "$body" -w '%{http_code}' "${base}/accounts/login/" || true)"

case "$code" in
  200|301|302) ;;
  *)
    echo "unexpected HTTP ${code} from Seafile login page" >&2
    exit 1
    ;;
esac

if ! grep -qi 'seafile' "$body"; then
  echo "response does not look like a Seafile login page" >&2
  exit 1
fi

echo "Seafile login page responded with HTTP ${code}"
