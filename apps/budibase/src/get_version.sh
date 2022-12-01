echo "budibase version:"$(docker exec -i budibase grep "version" package.json|head -n 1|awk -F ":" '{print $2}')>> /data/logs/install_version.txt
