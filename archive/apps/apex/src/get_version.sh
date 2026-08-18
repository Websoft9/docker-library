sudo echo "apex version:" $(docker exec -i apex ls /opt/oracle/apex|grep -v images|grep -v setapexadmin.sql) 1>> /data/logs/install_version.txt
