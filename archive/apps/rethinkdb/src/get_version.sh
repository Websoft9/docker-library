sudo echo $(docker exec -i $1 rethinkdb --version) |sudo  tee -a /data/logs/install_version.txt
