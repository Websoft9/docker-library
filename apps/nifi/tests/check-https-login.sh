#!/usr/bin/env bash
set -euo pipefail

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

base_url="${BASE_URL:-}"
if [ -z "${base_url}" ]; then
    base_url="https://localhost:${W9_HTTPS_PORT_SET}"
fi

curl -ksSL "${base_url}" -o "${tmp_file}"
grep -Eiq 'Apache NiFi|NiFi' "${tmp_file}"
