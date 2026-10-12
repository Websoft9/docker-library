#!/usr/bin/env bash
set -euo pipefail

base="${BASE_URL:?BASE_URL is required}"
body="$(mktemp)"
trap 'rm -f "$body"' EXIT

code="$(curl -sS -L -o "$body" -w '%{http_code}' "${base}/" || true)"

case "$code" in
  200|302) ;;
  *)
    echo "unexpected HTTP ${code} from Graylog web UI" >&2
    exit 1
    ;;
esac

if ! grep -Eqi 'graylog|initial configuration|sign in|login' "$body"; then
  echo "response does not look like a Graylog setup or login page" >&2
  exit 1
fi

echo "Graylog web UI responded with HTTP ${code}"
