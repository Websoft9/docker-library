#!/bin/bash
haproxpwd=$(grep "APP_PASSWORD" /data/apps/haproxy/.env |cut -d= -f2)
sudo sed -i "s/admin:.*/admin:$haproxpwd/g" /data/apps/haproxy/src/haproxy.cfg
cd /data/apps/haproxy
docker compose down -v
docker compose up -d

