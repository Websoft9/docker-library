#!/bin/bash
status="000"
echo "starting......"
while [ $status == "000" ]
do
        status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
        sleep 20
done
sleep 10
status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
echo "$status"
echo "startup complete"
echo "begin to load chinese..."
password=$1
export password
sudo docker exec apex /bin/bash -c "
cd /opt/oracle/apex/*/builder/zh-cn && NLS_LANG=Chinese_Chinese.AL32UTF8 && echo exit | /opt/oracle/sqlcl/bin/sql sys/"$password"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql
"
echo "finished"
