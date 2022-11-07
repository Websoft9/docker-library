#!/bin/bash
public_ip=`wget -O - https://download.websoft9.com/ansible/get_ip.sh | bash`

# add nginx.conf
sudo sed -i "s/example.domain.com/$public_ip/g" /data/apps/runtime/src/nginx/cockpit-proxy.conf
cp /data/apps/runtime/src/nginx/cockpit-proxy.conf /var/lib/docker/volumes/runtime_nginx_data/_data/nginx/proxy_host/websoft9.conf

docker restart nginx-proxy-manager

echo "nginx_proxy_port: 9001" >> /credentials/password.txt
echo "nginx_proxy_user: admin@example.com" >> /credentials/password.txt
echo "nginx_proxy_password: changeme" >> /credentials/password.txt
docker stop java8 java11 java13 java14 java15 java18 java19
