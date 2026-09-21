#!/usr/bin/env bash
set -euo pipefail

# Script cases run on the deployment target (see docs/app-tests.md). This builds
# a tiny WAR inside the Tomcat container, drops it into webapps/, waits for
# Tomcat to auto-deploy it, and verifies the context serves the expected page.

container="${W9_ID:?W9_ID is required}"
base="${BASE_URL:?BASE_URL is required}"
context="w9smoke"

cleanup() {
  docker exec "${container}" rm -f "/usr/local/tomcat/webapps/${context}.war" >/dev/null 2>&1 || true
  docker exec "${container}" rm -rf "/usr/local/tomcat/webapps/${context}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

cleanup

docker exec "${container}" bash -c '
  set -e
  rm -rf /tmp/w9src /tmp/w9smoke.war
  mkdir -p /tmp/w9src/WEB-INF
  printf "%s\n" "<!doctype html><h1>Websoft9 WAR smoke OK</h1>" > /tmp/w9src/index.html
  ( cd /tmp/w9src && jar cf /tmp/w9smoke.war . )
  cp /tmp/w9smoke.war /usr/local/tomcat/webapps/w9smoke.war
'

deadline=$((SECONDS + 120))
code="000"
while [ "${SECONDS}" -lt "${deadline}" ]; do
  code="$(curl -s -o /tmp/w9war.html -w '%{http_code}' --max-time 10 "${base}/${context}/" || true)"
  [ "${code}" = "200" ] && break
  sleep 3
done

if [ "${code}" != "200" ]; then
  echo "WAR context /${context}/ -> ${code} (timeout)" >&2
  exit 1
fi

if ! grep -q "Websoft9 WAR smoke OK" /tmp/w9war.html; then
  echo "WAR context served unexpected body:" >&2
  cat /tmp/w9war.html >&2
  exit 1
fi

echo "WAR auto-deploy ok at ${base}/${context}/"
