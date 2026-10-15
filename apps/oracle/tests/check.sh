#!/usr/bin/env bash
# Oracle XE first boot initializes the database, which can take several minutes;
# custom cases are not auto-retried by the harness, so poll here.
set -u

container="${W9_ID:?W9_ID is required}"

deadline=$((SECONDS + 900))
while [ "${SECONDS}" -lt "${deadline}" ]; do
  if docker exec "${container}" bash -c 'exec 3<>/dev/tcp/127.0.0.1/1521' 2>/dev/null; then
    echo "Oracle database listener is accepting connections on 1521"
    exit 0
  fi
  sleep 10
done

echo "Oracle database listener did not accept connections before timeout" >&2
exit 1
