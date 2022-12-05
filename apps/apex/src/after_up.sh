#!/bin/bash
status="000"
echo "sleep start" >> /tmp/debug.txt
sleep 600s
echo "sleep end" >> /tmp/debug.txt
while [ $status == "000" ]
do
        echo 'starting.....'
        status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
        sleep 15
done
echo "$status" >> /tmp/debug.txt
echo "startup complete"  >> /tmp/debug.txt
export password=$(grep "apex_db_oracle_password" /credentials/password.txt|awk -F ": " '{print $2}')
echo "begin to load chinese..."
sudo docker exec -it apex /bin/bash -c "
cd /opt/oracle/apex/*/builder/zh-cn
NLS_LANG=Chinese_Chinese.AL32UTF8
echo exit | /opt/oracle/sqlcl/bin/sql sys/"$password"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql
"
echo "finished"  >> /tmp/debug.txt
