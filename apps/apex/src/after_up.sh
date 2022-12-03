#!/bin/bash
while ( ! [ -n $(docker ps -q -f "name=^apex$") ] )
do
        echo "starting..."
        sleep 2
done

sudo docker exec -it apex /bin/bash -c "
dirpath="/opt/oracle/apex/*/builder/zh-cn"
filename="/opt/oracle/sqlcl/bin/sql"
while ( [ ! -d "$dirpath" ] && [ ! -e "$filename" ] )
do
        echo "starting......"
        sleep 2
done"
echo "startup complete"
export password=$(grep "apex_db_oracle_password" /credentials/password.txt|awk -F ": " '{print $2}')
echo "begin to load chinese..."
sudo docker exec -it apex /bin/bash -c "      
cd /opt/oracle/apex/*/builder/zh-cn
NLS_LANG=Chinese_Chinese.AL32UTF8 
echo exit | /opt/oracle/sqlcl/bin/sql sys/"$password"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql
"
echo "finished"
