sudo echo "oracle version:" $(docker exec -i $1 ls /opt/oracle/product)  1>> /data/logs/install_version.txt
