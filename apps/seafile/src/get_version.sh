sudo echo "seafile version:" $(docker inspect seafile |grep -i seafile_version |cut -d= -f2) |sudo tee -a /data/logs/install_version.txt
