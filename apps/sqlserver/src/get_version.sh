sudo echo "sqlserver version:" $(cat /data/apps/sqlserver/.env |grep -i "APP_VERSION" |awk -F "=" '{print  $2}') |sudo tee -a /data/logs/install_version.txt
