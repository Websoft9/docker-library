sudo echo "wordpress version:" $(docker exec -i $1 cat /var/www/html/wp-includes/version.php |grep "wp_version ="|awk -F"= " '{print $2}') |sudo tee -a /data/logs/install_version.txt
