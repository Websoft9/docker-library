sudo echo "matomo version:" $(docker exec -it $1 cat /var/www/html/core/Version.php|grep "const VERSION ="|cut -d"=" -f2) |sudo tee -a /data/logs/install_version.txt
