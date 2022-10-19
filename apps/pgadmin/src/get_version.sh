sudo echo "pgadmin version $(docker exec -i $1 sh -c 'cat docs/release_notes.html  |grep -i version |tail -1 |cut -d= -f4')" 1>> /data/logs/install_version.txt
