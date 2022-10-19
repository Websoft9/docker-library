sudo echo "cloudbeaver version: $(docker exec -i $1 sed -n '3p' /opt/cloudbeaver/server/readme.txt)" 1>> /data/logs/install_version.txt
