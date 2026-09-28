#!/bin/bash
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin


#--------------------
# Set you port
#--------------------


# Set the filename
filename=".env"

# Read the value of W9_UDP_PORT from the file
port=$(grep -oP 'W9_UDP_PORT=\K\d+' "$filename")

# Increment the value by 1
new_port=$((port + 1))

# Replace the old value with the new value in the file
sed -i "s/W9_UDP_PORT=$port/W9_UDP_PORT=$new_port/" "$filename"

cat .env
sudo docker down -v
sudo docker compose up -d
sleep 10s

#--------------------------------------------
# Copy keys to data directory
#--------------------------------------------

rm -rf /data/keys
cp -r /var/lib/docker/volumes/wireguard_wireguard/_data/  /data/keys
chmod -R 0755 /data/keys
