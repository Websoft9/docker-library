How to install zabbix-agent in ubuntu

a. Install Zabbix repository
   wget https://repo.zabbix.com/zabbix/6.4/ubuntu/pool/main/z/zabbix-release/zabbix-release_6.4-1+ubuntu22.04_all.deb
   dpkg -i zabbix-release_6.4-1+ubuntu22.04_all.deb
   apt update

b. Install Zabbix agent
   apt install zabbix-agent

c. Config Zabbix agent
 - Get zabbix-server IP Address
   docker inspect <zabbix-server-contain-id> | grep IPA
 - Modify zabbix-aegnt config file
   vim /etc/zabbix/zabbix_agentd.conf
 - Replace zabbix server IP
   Server=<zabbix-server-ip>
   ServerActive=<zabbix-server-ip>
 - Restart zabbix agent
   systemctl restart zabbix-agent
