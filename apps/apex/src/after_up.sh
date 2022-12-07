#!/bin/bash
status="000"
echo "starting......" >> /tmp/debug.txt
sudo sh -c 'echo "init-password started at" $(date -d now)  1>> /tmp/debug.txt'
while [ $status == "000" ]
do
        status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
        sleep 20
done
sudo sh -c 'echo "init-password started at" $(date -d now)  1>> /tmp/debug.txt'
echo "$status" >> /tmp/debug.txt
echo "startup complete" >> /tmp/debug.txt
sleep 10
echo "begin to load chinese..." >> /tmp/debug.txt
export $1
sudo docker exec -it apex /bin/bash -c "
echo $1 >> /tmp/debug.txt && cd /opt/oracle/apex/*/builder/zh-cn && NLS_LANG=Chinese_Chinese.AL32UTF8 && echo exit | /opt/oracle/sqlcl/bin/sql sys/"$1"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql >> /tmp/debug.txt
"
echo "finished" >> /tmp/debug.txt
