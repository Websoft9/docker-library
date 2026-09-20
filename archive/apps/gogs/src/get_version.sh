sudo echo  $(sudo docker exec -it gogs ./gogs --version) |sudo  tee -a /data/logs/install_version.txt
