#!/usr/bin/env bash
set -euo pipefail

container_name="${W9_ID}"
members_output="$(docker exec "${container_name}" consul members)"

if [[ -z "${members_output}" ]]; then
  echo "consul members returned empty output"
  exit 1
fi

if ! grep -Eq 'alive' <<<"${members_output}"; then
  echo "no alive consul member reported"
  exit 1
fi
