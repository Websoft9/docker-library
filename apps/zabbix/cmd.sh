#!/bin/bash

echo "##########################################start set init password#################################################################"
apt-get update && apt-get install apache2-utils -y 1>/dev/null 2>&1

# for CentOS image
# yum install httpd-tools -y 1>/dev/null 2>&1

app_pass=$(htpasswd -bnBC 10 "" $W9_LOGIN_PASSWORD | tr -d ':')
app_pass=$(echo $app_pass |sed 's/\$/\\$/g')
app_pass=$(echo $app_pass |sed 's/\//\\\//g')
echo $app_pass

cd /usr/share/doc/zabbix-server-mysql
gunzip create.sql.gz
sed -i "s/\$2y\$10\$92nDno4n0Zm7Ej7Jfsz8WukBfgSS\/U0QkIuu8WkJPihXBb2A1UrEK/$app_pass/g" create.sql
gzip create.sql
/usr/bin/tini -- /usr/bin/docker-entrypoint.sh /usr/sbin/zabbix_server --foreground -c/etc/zabbix/zabbix_server.conf
