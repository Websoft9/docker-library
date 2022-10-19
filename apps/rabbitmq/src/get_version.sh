sudo echo "rabbitmq version:" $(docker exec -i $1 rabbitmqctl version) |sudo tee -a /data/logs/install_version.txt
