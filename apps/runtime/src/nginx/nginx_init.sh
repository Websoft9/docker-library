#!/bin/bash

# add nginx.conf
cp /data/apps/runtime/src/nginx/1.conf /var/lib/docker/volumes/runtime_nginx_data/_data/nginx/proxy_host

cd /data/apps/runtime/src/nginx && echo sqlite3 database.sqlite
