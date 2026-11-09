#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:?W9_ID is required}"
port=28015

deadline=$((SECONDS + 180))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  if docker exec "${container}" timeout 10 bash -c "exec 3<>/dev/tcp/127.0.0.1/${port}" 2>/dev/null; then
    echo "RethinkDB driver port accepted a connection"
    exit 0
  fi
  sleep 5
done

echo "RethinkDB driver port did not accept a connection before timeout" >&2
exit 1
