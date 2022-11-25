#!/bin/bash

# create by Websoft9
# Replace DB connetion
if [[ ! -f "/var/www/html/layouts/v7/modules/Install/Step4.tpl" ]]; then
   echo "Initialization has been completed before this time!"
else
    
   db_hostname=$(grep -n DB_HOSTNAME /var/www/html/layouts/v7/modules/Install/Step4.tpl |cut -d ":" -f1)
   sed -i "$db_hostname s/text/hidden/g" /var/www/html/layouts/v7/modules/Install/Step4.tpl
   sed -i 's/DB_HOSTNAME.*/VTIGER_DB_HOST}" name="db_hostname">${VTIGER_DB_HOST}<\/td>/g' /var/www/html/layouts/v7/modules/Install/Step4.tpl

   db_user=$(grep -n DB_USER /var/www/html/layouts/v7/modules/Install/Step4.tpl |cut -d ":" -f1)
   sed -i "$db_user s/text/hidden/g" /var/www/html/layouts/v7/modules/Install/Step4.tpl
   sed -i 's/DB_USER.*/VTIGER_DB_USER}" name="db_username">${VTIGER_DB_USER}<\/td>/g' /var/www/html/layouts/v7/modules/Install/Step4.tpl


  db_password=$(grep -n DB_PASSWORD /var/www/html/layouts/v7/modules/Install/Step4.tpl |cut -d ":" -f1)
  sed -i "$db_password s/password/hidden/g" /var/www/html/layouts/v7/modules/Install/Step4.tpl
  sed -i 's/DB_PASSWORD.*/VTIGER_DB_PASSWORD}" name="db_password">${VTIGER_DB_PASSWORD}<\/td>/g' /var/www/html/layouts/v7/modules/Install/Step4.tpl


  db_name=$(grep -n DB_NAME} /var/www/html/layouts/v7/modules/Install/Step4.tpl |cut -d ":" -f1)
  sed -i "$db_name s/text/hidden/g" /var/www/html/layouts/v7/modules/Install/Step4.tpl
  sed -i 's/DB_NAME}.*/VTIGER_DB_DATABASE}" name="db_name">${VTIGER_DB_DATABASE}<\/td>/g' /var/www/html/layouts/v7/modules/Install/Step4.tpl
fi

docker-php-entrypoint apache2-foreground
# Install wizard
