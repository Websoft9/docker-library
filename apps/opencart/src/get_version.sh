sudo echo "opencart version:" $(docker exec -i $1 cat /opt/bitnami/opencart/index.php  |grep VERSION |cut -d"'" -f4) |sudo tee -a /data/logs/install_version.txt
