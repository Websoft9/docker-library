sudo echo "webmin version:" $(docker exec -i $1 cat /etc/webmin/version) |tee -a /data/logs/install_version.txt
