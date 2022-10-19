sudo echo "erpnext version:" $(cat /data/apps/erpnext/.env |grep  "APP_VERSION" |awk -F"=" '{print $2}') 1>> /data/logs/install_version.txt
