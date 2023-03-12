sudo echo "apitable" $(docker exec -it apitable-web-server-1 cat package.json|grep version) 1>> /data/logs/install_version.txt
