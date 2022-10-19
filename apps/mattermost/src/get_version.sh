sudo echo "Mattermost version:" $(docker exec -i $1 cat /bitnami/mattermost/bin/mattermost version |grep Version  |head -1 |cut -d: -f2)" 1>> /data/logs/install_version.txt
