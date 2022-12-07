#!/bin/bash
status="000"
echo "starting......" >> /tmp/debug.txt
while [ $status == "000" ]
do
        status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
        sleep 15
done
echo "$status" >> /tmp/debug.txt
echo "startup complete" >> /tmp/debug.txt
echo "getting password..." >> /tmp/debug.txt
echo $1 >> /tmp/password.txt
docker cp /tmp/password.txt apex:/tmp/password.txt
echo "begin to load chinese..." >> /tmp/debug.txt
sudo docker exec -it apex /bin/bash -c "
password=$(cat /tmp/password.txt)      
cd /opt/oracle/apex/*/builder/zh-cn
NLS_LANG=Chinese_Chinese.AL32UTF8 
echo exit | /opt/oracle/sqlcl/bin/sql sys/"$password"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql >> /tmp/debug.txt
"
echo "finished" >> /tmp/debug.txt
