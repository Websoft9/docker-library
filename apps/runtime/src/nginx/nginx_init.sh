#!/bin/bash
sudo chmod +x /data/apps/runtime/src/nginx/gitip.sh
public_ip=$(bash /data/apps/runtime/src/nginx/gitip.sh)

# add nginx.conf
sudo sed -i "s/example.domain.com/$public_ip/g" /data/apps/runtime/src/nginx/cockpit-proxy.conf
cp /data/apps/runtime/src/nginx/cockpit-proxy.conf /var/lib/docker/volumes/runtime_nginx_data/_data/nginx/proxy_host/1.conf

# update db record
cd /data/apps/runtime/src/nginx && echo "update proxy_host set domain_names='[\"$public_ip\"]';" | sqlite3 database.sqlite
rm -f /var/lib/docker/volumes/runtime_nginx_data/_data/database.sqlite
cp /data/apps/runtime/src/nginx/database.sqlite /var/lib/docker/volumes/runtime_nginx_data/_data

docker restart nginx-proxy-manager

echo "nginx_proxy_port: 9001" >> /credentials/password.txt
echo "nginx_proxy_user: admin@example.com" >> /credentials/password.txt
echo "nginx_proxy_password: changeme" >> /credentials/password.txt
docker stop java8 java11 java13 java14 java15 java18 java19
