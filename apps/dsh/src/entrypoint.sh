#!/bin/sh
set -eu

: "${W9_HTTP_PORT:=3080}"
: "${DSH_INTERNAL_PORT:=3081}"
: "${DSH_HOME:=/var/lib/dsh}"
: "${DSH_WORKSPACE:=/workspace}"
: "${DSH_FORCE_LOOPBACK_UI:=true}"
: "${W9_URL:=}"
: "${DSH_TRUSTED_HOSTS:=}"

mkdir -p "${DSH_HOME}" "${DSH_WORKSPACE}"

cd "${DSH_WORKSPACE}"

trusted_host_args=""
if [ -n "${W9_URL}" ]; then
  trusted_host=$(printf '%s' "${W9_URL}" | sed -E 's#^[a-zA-Z]+://##; s#/.*$##')
  if [ -n "${trusted_host}" ]; then
    trusted_host_args="--trusted-host ${trusted_host}"
  fi
fi

if [ -n "${DSH_TRUSTED_HOSTS}" ]; then
  OLD_IFS=${IFS}
  IFS=,
  set -- ${DSH_TRUSTED_HOSTS}
  IFS=${OLD_IFS}
  for raw_host in "$@"; do
    extra_host=$(printf '%s' "${raw_host}" | sed -E 's#^[[:space:]]+##; s#[[:space:]]+$##; s#^[a-zA-Z]+://##; s#/.*$##')
    if [ -n "${extra_host}" ]; then
      trusted_host_args="${trusted_host_args} --trusted-host ${extra_host}"
    fi
  done
fi

local_app_flag=false
case "$(printf '%s' "${DSH_FORCE_LOOPBACK_UI}" | tr '[:upper:]' '[:lower:]')" in
  true|1|yes|on)
    local_app_flag=true
    ;;
esac

local_app_script="<script>window.__DSH_LOCAL_APP__ = ${local_app_flag};</script>"
escaped_local_app_script=$(printf '%s' "${local_app_script}" | sed 's/[\/&]/\\&/g')
sed "s/__DSH_LOCAL_APP_SCRIPT__/${escaped_local_app_script}/g" /etc/nginx/nginx.conf > /tmp/nginx.conf
mv /tmp/nginx.conf /etc/nginx/nginx.conf

# Preserve the external browser authority through the reverse proxy. DSH rejects
# non-loopback API requests unless their Host/Origin are listed as trusted.
# shellcheck disable=SC2086
dsh web --host 127.0.0.1 --port "${DSH_INTERNAL_PORT}" --no-open ${trusted_host_args} &
dsh_pid=$!

ready=false
for _ in $(seq 1 60); do
  status_code=$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${DSH_INTERNAL_PORT}/" || true)
  if [ "${status_code}" = "200" ] || [ "${status_code}" = "401" ]; then
    ready=true
    break
  fi
  if ! kill -0 "${dsh_pid}" >/dev/null 2>&1; then
    wait "${dsh_pid}"
    exit 1
  fi
  sleep 1
done

if [ "${ready}" != "true" ]; then
  echo "dsh web did not become ready on 127.0.0.1:${DSH_INTERNAL_PORT} within 60 seconds" >&2
  kill "${dsh_pid}" >/dev/null 2>&1 || true
  wait "${dsh_pid}" >/dev/null 2>&1 || true
  exit 1
fi

exec nginx -g 'daemon off;'
