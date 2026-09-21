#!/bin/bash
set -euo pipefail

APP_DIR="${APP_DIR:-/usr/local/tomcat}"
cd "${APP_DIR}"

exec catalina.sh run
