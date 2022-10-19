echo "rocketchat version:" $(cat /data/apps/rocketchat/.env |grep APP_VERSION |awk -F"=" '{print $2}') >> /data/logs/install_version.txt
