sudo echo "dolibarr version:" $(docker images |grep tuxgasy/dolibarr |awk '{print $2}')  1>> /data/logs/install_version.txt
