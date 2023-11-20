activemqkind=$(docker image list|grep ghcr)
if [[ $activemqkind == "" ]] ; then
  sudo echo "activemq version:" $(docker exec -it $1  find /opt/activemq -name activemq-all* | cut -d- -f3) | sudo tee -a /data/logs/install_version.txt
else
  sudo echo "activemq version:" $(cat /data/apps/activemq/.env |grep W9_ARTEMIS_VERSION |cut -d= -f2) | sudo tee -a /data/logs/install_version.txt
fi 
