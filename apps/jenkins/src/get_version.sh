sudo echo jenkins version: $(docker exec -i $1 cat /var/jenkins_home/config.xml |grep version |sed -n 2p |tr -d "</>version") |sudo tee -a /data/logs/install_version.txt
