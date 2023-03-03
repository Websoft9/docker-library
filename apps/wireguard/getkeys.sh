#!/bin/bash
export PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin:/usr/local/bin

#--------------------------------------------
# Copy keys to data directory
#--------------------------------------------

rm -rf /data/keys
cp -r /var/lib/docker/volumes/wireguard_wireguard/_data/  /data/keys
chmod -R 0755 /data/keys
