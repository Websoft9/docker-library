sudo echo "Mattermost version:" $(sudo docker exec -i mattermost /mattermost/bin/mattermost version|grep  -i "version" | cut -d ":" -f 2) |sudo tee -a /data/logs/install_version.txt
