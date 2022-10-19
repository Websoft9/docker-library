sudo echo Phpmyadmin Version:$(docker exec -i $1 bash -c 'cat /var/www/html/package.json | grep version') 1>> /data/logs/install_version.txt
