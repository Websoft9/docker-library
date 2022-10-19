sudo echo "couchdb version:" $(docker exec -i $1 cat /opt/couchdb/releases/RELEASES  |sed -n 2p | awk -F '"' '{print $4}') |sudo tee -a /data/logs/install_version.txt
