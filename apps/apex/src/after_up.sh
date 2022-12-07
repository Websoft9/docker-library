#!/bin/bash
status="000"
echo "starting......" >> /tmp/debug.txt
sudo sh -c 'echo "started at" $(date -d now)  1>> /tmp/debug.txt'
while [ $status == "000" ]
do
        status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
        sleep 20
done
sleep 10
sudo sh -c 'echo "ended at" $(date -d now)  1>> /tmp/debug.txt'
status=$(curl -IL -m 5 -s -w "%{http_code}\n" -o /dev/null "localhost:9001")
echo "$status" >> /tmp/debug.txt
echo "startup complete" >> /tmp/debug.txt
echo "begin to load chinese..." >> /tmp/debug.txt
password=$1
echo $password >> /tmp/debug.txt
export password
sudo sh -c 'echo "started at" $(date -d now)  1>> /tmp/debug.txt'
sudo docker exec apex /bin/bash -c "
cd /opt/oracle/apex/*/builder/zh-cn && NLS_LANG=Chinese_Chinese.AL32UTF8 && echo exit | /opt/oracle/sqlcl/bin/sql sys/"$password"@apex-db:1521/xepdb1 as sysdba @load_zh-cn.sql
" >> /tmp/debug.txt
sudo sh -c 'echo "ended at" $(date -d now)  1>> /tmp/debug.txt'
echo "finished" >> /tmp/debug.txt
