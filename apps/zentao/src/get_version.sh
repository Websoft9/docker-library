sudo echo "zootao version:" $(docker exec -i $1 cat /var/www/zentaopms/VERSION) |tee -a /data/logs/install_version.txt
