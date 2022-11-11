#!/bin/bash
# customrized cmd powered by websoft9

if [ ! -f "/var/www/html/install/controller/install/step_3.php" ];then
  echo "The initialization file does not exist，The initialization action is no longer performed!"
else
  echo "The initialization file  exists，Perform an initialization action"
  cd /var/www/html/install/controller/install

  db_hostname=$(grep -nw '$data\['\''db_hostname'\''\] = '\''localhost'\' step_3.php| awk -F ":" '{print $1}')
  sed -i "$db_hostname s/'localhost'/'$MYSQL_HOST'/" step_3.php

  db_username=$(grep -nw '$data\['\''db_username'\''\] = '\''root'\' step_3.php| awk -F ":" '{print $1}')
  sed -i "$db_username s/'root'/'$MYSQL_USER'/" step_3.php

  db_password=$(grep -nw '$data\['\''db_password'\''\] = '\'\' step_3.php| awk -F ":" '{print $1}')
  sed -i "$db_password s/''/'$MYSQL_PASSWORD'/" step_3.php

  db_database=$(grep -nw '$data\['\''db_database'\''\] = '\'\' step_3.php| awk -F ":" '{print $1}')
  sed -i "$db_database s/''/'$MYSQL_DATABASE'/" step_3.php
fi
docker-php-entrypoint apache2-foreground
