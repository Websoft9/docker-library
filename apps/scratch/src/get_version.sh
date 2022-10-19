sudo echo "Scratch version:" $(docker exec -i scratch grep -rn "Scratch" /usr/share/nginx/html/index.html |awk -F"<title>" '{print$2}'|awk -F"</title>" '{print$1}') 1>> /data/logs/install_version.txt
