#!/usr/bin/env bash
set -euo pipefail

status="$(curl -s -o /dev/null -w '%{http_code}' "${BASE_URL}/")"
if [ "${status}" != "200" ]; then
  echo "unexpected status from ${BASE_URL}/: ${status}" >&2
  exit 1
fi

headers="$(curl -sI "${BASE_URL}/")"
if ! grep -qi '^varnish-default-vcl: true' <<<"${headers}"; then
  echo "missing varnish-default-vcl header" >&2
  exit 1
fi
if ! grep -qi '^via: .*Varnish/' <<<"${headers}"; then
  echo "missing Via: ... Varnish header" >&2
  exit 1
fi

echo "varnish serving ${BASE_URL}/ (status=${status})"
