sudo echo "$(docker exec -i $1 occ -Version)" |sudo tee -a /data/logs/install_version.txt
