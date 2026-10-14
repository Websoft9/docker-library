#!/usr/bin/env bash
# Elasticsearch first boot can take over a minute, and custom cases are not
# auto-retried by the harness, so poll the cluster health endpoint here.
# The API is plain HTTP with basic auth; TLS is terminated by the platform.
set -u

port="${W9_HTTP_PORT_SET:-9200}"
user="${W9_LOGIN_USER:-elastic}"
pass="${W9_LOGIN_PASSWORD:-${W9_POWER_PASSWORD:-}}"

code=""
for _ in $(seq 1 30); do
  code="$(curl -s -o /dev/null -w '%{http_code}' -u "${user}:${pass}" "http://localhost:${port}/_cluster/health" 2>/dev/null || true)"
  if [ "${code}" = "200" ]; then
    echo "elasticsearch cluster health ok"
    exit 0
  fi
  sleep 5
done

echo "elasticsearch cluster health returned HTTP ${code}" >&2
exit 1
