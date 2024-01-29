sudo echo "erpnext version:" $(docker exec -i erpnext cat /home/frappe/frappe-bench/apps/erpnext/erpnext/__init__.py|grep version |cut -d "=" -f2) 1>> /data/logs/install_version.txt
