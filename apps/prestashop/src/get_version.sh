sudo echo "prestashop version:" $(docker exec -i $1 cat /var/www/html/app/AppKernel.php|grep "const VERSION"|cut -d= -f2) 1>> /data/logs/install_version.txt
