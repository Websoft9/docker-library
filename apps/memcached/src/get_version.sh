sudo echo $(docker exec -i $1 memcached --version)" 1>> /data/logs/install_version.txt
