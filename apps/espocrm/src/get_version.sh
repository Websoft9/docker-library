sudo echo espocrm version:$(docker exec -i espocrm cat /var/www/html/data/config.php|grep "'version' =>" |cut -d">" -f2) 1>> /data/logs/install_version.txt
