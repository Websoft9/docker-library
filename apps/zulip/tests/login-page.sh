#!/bin/sh
set -eu

base_url="${BASE_URL:-}"
if [ -z "${base_url}" ]; then
  base_url="https://127.0.0.1:${W9_HTTPS_PORT_SET}"
fi

curl -kfsSL "${base_url}/login/" | grep -qi "zulip"
