sudo echo Redis Version:$(docker exec -i $1 /usr/local/bin/redis-server -v) 1>> /data/logs/install_version.txt
