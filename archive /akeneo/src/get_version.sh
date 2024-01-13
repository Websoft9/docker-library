sudo echo "akeneo version:" $(docker exec -i $1 grep "pim-community-dev/tree" /var/www/html/composer.lock |awk -F"/v" '{print $2}') 1>> /data/logs/install_version.txt
