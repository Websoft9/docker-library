#!/bin/bash

public_ip=bash /data/apps/runtime/src/nginx/gitip.sh

# add nginx.conf
sudo sed -i "s/$example.domain.com/$public_ip/g" /data/apps/runtime/src/nginx/1.conf
cp /data/apps/runtime/src/nginx/1.conf /var/lib/docker/volumes/runtime_nginx_data/_data/nginx/proxy_host

cd /data/apps/runtime/src/nginx && echo "update proxy_host set domain_names='[\"$public_ip\"]';" | sqlite3 database.sqlite
