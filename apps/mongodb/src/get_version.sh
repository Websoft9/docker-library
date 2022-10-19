sudo echo "MongoDB version:" $(docker exec -i $1 mongo --version | grep MongoDB) 1>> /data/logs/install_version.txt
