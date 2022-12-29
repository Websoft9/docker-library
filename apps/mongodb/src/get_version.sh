sudo echo "MongoDB version:" $(docker exec -i $1 mongod --version | grep db | cut -d " " -f 3) >> /data/logs/install_version.txt
