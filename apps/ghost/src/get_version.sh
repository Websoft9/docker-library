sudo echo "ghost_version:" $(docker exec -it $1 ls versions) |sudo tee -a /data/logs/install_version.txt
