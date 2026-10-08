echo "rocketchat version:" $(cat /data/apps/rocketchat/.env |grep W9_VERSION |awk -F"=" '{print $2}') >> /data/logs/install_version.txt
