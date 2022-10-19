sudo echo kong version: $(docker exec -i $1 kong version) |sudo tee -a /data/logs/install_version.txt
