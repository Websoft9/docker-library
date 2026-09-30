#!/usr/bin/env bash
set -euo pipefail

tmp_file="$(mktemp)"
trap 'rm -f "${tmp_file}"' EXIT

curl -fsSL "${BASE_URL}" -o "${tmp_file}"
grep -qi "EspoCRM" "${tmp_file}"
