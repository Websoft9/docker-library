sudo echo "minio version:" $(docker inspect $1 | grep '"version":'|cut -d ':' -f 2) |sudo tee -a /data/logs/install_version.txt
