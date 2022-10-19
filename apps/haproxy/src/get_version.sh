sudo echo "haproxy version:" $(docker exec -i $1 haproxy -v | grep "version" | awk -F" " '{print $3}') |sudo tee -a /data/logs/install_version.txt
