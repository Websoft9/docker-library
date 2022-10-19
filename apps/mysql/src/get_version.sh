# | awk "{print \$5}" | awk -F"-" "{print \$1}"
sudo echo MySQL Version:$(docker exec -it $1 mysql -V ) 1>> /data/logs/install_version.txt
