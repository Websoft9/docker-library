 sudo echo "zabbix version:" $(docker images |grep zabbix-server |cut -d- -f4) |sudo tee -a /data/logs/install_version.txt
