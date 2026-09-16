#!/bin/bash
set -e

WORKSPACE=/workspace
TEMPLATE=/opt/template

case "${W9_VERSION:-}" in
  ""|latest|main|stable) SPRING_BOOT_VERSION="4.1.1" ;;
  *) SPRING_BOOT_VERSION="${W9_VERSION}" ;;
esac

DB_ENABLED=0
case ",${COMPOSE_PROFILES:-}," in
  *,postgres,*) DB_ENABLED=1 ;;
esac

mkdir -p "$WORKSPACE"

if [ ! -f "$WORKSPACE/pom.xml" ]; then
  echo "No Maven project found; creating a default Spring Boot project (${SPRING_BOOT_VERSION})..."
  cp -a "$TEMPLATE/." "$WORKSPACE/"
  sed -i "s/@SPRING_BOOT_VERSION@/${SPRING_BOOT_VERSION}/g" "$WORKSPACE/pom.xml"
  echo "$SPRING_BOOT_VERSION" > "$WORKSPACE/.w9-springboot-version"
  echo "Default project created in /workspace. Edit the code, then run: mvn spring-boot:run"
fi

cd "$WORKSPACE"

if [ "$DB_ENABLED" = "1" ]; then
  case ",${SPRING_PROFILES_ACTIVE:-}," in
    *,postgres,*) ;;
    *) SPRING_PROFILES_ACTIVE="${SPRING_PROFILES_ACTIVE:+${SPRING_PROFILES_ACTIVE},}postgres" ;;
  esac
  export SPRING_PROFILES_ACTIVE
  echo "PostgreSQL enabled; waiting for ${W9_ID}-postgresql:5432 ..."
  for _ in $(seq 1 60); do
    if (echo > "/dev/tcp/${W9_ID}-postgresql/5432") >/dev/null 2>&1; then
      echo "PostgreSQL is reachable."
      break
    fi
    sleep 2
  done
  exec mvn -q -DskipTests -Ppostgres spring-boot:run
fi

exec mvn -q -DskipTests spring-boot:run
