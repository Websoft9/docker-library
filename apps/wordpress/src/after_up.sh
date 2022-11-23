#!/bin/bash
sleep 10s

sudo docker cp /data/apps/wordpress/data/backup/wp-cli.phar wordpress:/tmp
sudo docker exec -it wordpress chmod +x /tmp/wp-cli.phar
sudo docker exec -it wordpress mv /tmp/wp-cli.phar /usr/local/bin/wp
