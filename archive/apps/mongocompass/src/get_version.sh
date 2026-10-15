sudo echo "mongocompass version:" $(docker ps --format '{{.Image}}'|grep mongocompass|awk -F":" '{print $2}') 1>> /data/logs/install_version.txt
