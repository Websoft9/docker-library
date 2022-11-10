sudo echo "Mattermost version:" $(docker exec -i mattermost /mattermost/bin/mattermost version)" 1>> /data/logs/install_version.txt
