#!/usr/bin/env bash
set -euo pipefail

curl -fsSL "${BASE_URL}/" | grep -qi "Couchbase Server"
