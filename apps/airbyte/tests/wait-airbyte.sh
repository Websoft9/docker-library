#!/usr/bin/env bash
set -euo pipefail

deadline=$((SECONDS + 1800))
url="${BASE_URL%/}/api/v1/health"

until curl -fsS "${url}" | grep -q '"available":true'; do
  if [ "${SECONDS}" -ge "${deadline}" ]; then
    echo "timed out waiting for ${url}" >&2
    exit 1
  fi
  sleep 10
done

echo "Airbyte health ready at ${url}"
