sudo echo "postgresql version: " $(docker exec -i $1 psql -V)  1>> /data/logs/install_version.txt
