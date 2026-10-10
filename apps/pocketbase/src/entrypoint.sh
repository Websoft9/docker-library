#!/bin/sh
set -eu

data_dir="${POCKETBASE_DIR:-/pb_data}"
http_port="${W9_HTTP_PORT:-8090}"

mkdir -p "${data_dir}"

if [ ! -f "${data_dir}/data.db" ] && [ -n "${W9_LOGIN_USER:-}" ] && [ -n "${W9_LOGIN_PASSWORD:-}" ]; then
  /usr/local/bin/pocketbase superuser create "${W9_LOGIN_USER}" "${W9_LOGIN_PASSWORD}" --dir="${data_dir}" || true
fi

exec /usr/local/bin/pocketbase serve --http="0.0.0.0:${http_port}" --dir="${data_dir}"
