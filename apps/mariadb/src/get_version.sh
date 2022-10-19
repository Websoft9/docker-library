sudo echo MariaDB Version:$(docker exec -it $1 mysql -V | awk "{print \$5}" | awk -F"-" "{print \$1}" ) 1>> /data/logs/install_version.txt
