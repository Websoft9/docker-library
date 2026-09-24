sudo echo "sqlserver version:" $(cat /data/apps/sqlserver/.env |grep -i "W9_VERSION" |awk -F "=" '{print  $2}') |sudo tee -a /data/logs/install_version.txt
