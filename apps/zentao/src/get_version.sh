sudo echo "zentao version:" $(docker exec -i $1 cat /apps/zentao/VERSION) |tee -a /data/logs/install_version.txt
