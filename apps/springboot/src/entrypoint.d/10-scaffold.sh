#!/bin/bash
set -euo pipefail

WORKSPACE="${APP_DIR:-/workspace}"
TEMPLATE=/opt/template

case "${W9_VERSION:-}" in
  ""|latest|main|stable) SPRING_BOOT_VERSION="4.1.1" ;;
  *) SPRING_BOOT_VERSION="${W9_VERSION}" ;;
esac

mkdir -p "$WORKSPACE"

if [ ! -f "$WORKSPACE/pom.xml" ]; then
  echo "[springboot-runtime] No Maven project found; creating a default Spring Boot project (${SPRING_BOOT_VERSION})..."
  cp -a "$TEMPLATE/." "$WORKSPACE/"
  sed -i "s/@SPRING_BOOT_VERSION@/${SPRING_BOOT_VERSION}/g" "$WORKSPACE/pom.xml"
  echo "Default project created in /workspace. Edit the code, then run: mvn spring-boot:run"
fi
