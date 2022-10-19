sudo echo $(docker exec -i $1 neo4j version) 1>> /data/logs/install_version.txt
