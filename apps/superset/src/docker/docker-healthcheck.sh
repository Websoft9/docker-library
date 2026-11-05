#!/usr/bin/env bash

curl -f "http://localhost:${SUPERSET_PORT}/${SUPERSET_APP_ROOT/\//}/health" || exit 1