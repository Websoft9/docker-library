#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

status="$(curl -sS -o "$body" -w '%{http_code}' "${base}/")"

# TeamCity serves HTTP 503 from its maintenance page until the first start is
# confirmed and the database connection is configured; it serves 200 afterwards.
case "$status" in
  200 | 503) ;;
  *)
    echo "unexpected HTTP ${status} from TeamCity" >&2
    exit 1
    ;;
esac

if ! grep -qi 'TeamCity' "$body"; then
  echo "response does not look like a TeamCity page" >&2
  exit 1
fi

echo "TeamCity server responded with HTTP ${status}"
