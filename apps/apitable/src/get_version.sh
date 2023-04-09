sudo echo "apitable" $(docker exec -it apitable-webserver sed -n '3p' package.json) |sudo tee -a /data/logs/install_version.txt 
