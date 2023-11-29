sudo systemctl stop nginx
cd /opt
chmod +x create_users.sh
MB_HOSTNAME=localhost MB_PORT=9001 W9_POWER_PASSWORD=$W9_POWER_PASSWORD ./create_users.sh
sudo systemctl start nginx
