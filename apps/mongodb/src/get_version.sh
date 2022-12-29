sudo echo "MongoDB version:" $(docker exec -i $1 mongod --version | grep db) 1>> /data/logs/install_version.txt
