#!/usr/bin/env bash
set -euo pipefail

container="${W9_ID:-grafana}"
stale_plugin="/var/lib/grafana/plugins/grafana-simple-json-datasource"

if docker exec "$container" test -d "$stale_plugin"; then
  echo "Unsupported stale plugin remains in the Grafana plugins volume: $stale_plugin" >&2
  echo "Remove that directory once before validating an existing instance." >&2
  exit 1
fi

started_at="$(docker inspect -f '{{.State.StartedAt}}' "$container")"
logs="$(docker logs --since "$started_at" "$container" 2>&1 || true)"

if grep -Eiq 'Plugin validation failed|angular plugins are not supported|Refusing to initialize plugin' <<<"$logs"; then
  echo "Grafana reported an unsupported plugin during this container startup." >&2
  grep -Ei 'Plugin validation failed|angular plugins are not supported|Refusing to initialize plugin' <<<"$logs" >&2
  exit 1
fi

echo "No unsupported plugin validation errors during the current startup."
