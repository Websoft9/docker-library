
#!/bin/bash

# create by Websoft9
# Replace DB connetion
if [[ ! -f "/var/www/html/layouts/v7/modules/Install/Step4.tpl" ]]; then
    echo "Initialization has been completed before this time!"
else
    
    cd /var/www/html/layouts/v7/modules/Install

    db_hostname=$(grep -n DB_HOSTNAME Step4.tpl |cut -d ":" -f1)
    sed -i "$db_hostname s/text/hidden/g" Step4.tpl
    sed -i "s/{\$DB_HOSTNAME}/$VTIGER_DB_HOST/g" Step4.tpl
    sed -i "s/db_hostname.*/db_hostname\">$VTIGER_DB_HOST<\/td>/g" Step4.tpl

    db_user=$(grep -n DB_USER Step4.tpl |cut -d ":" -f1)
    sed -i "$db_user s/text/hidden/g" Step4.tpl
    sed -i "s/{\$DB_USERNAME}/$VTIGER_DB_USER/g" Step4.tpl
    sed -i "s/db_username.*/db_username\">$VTIGER_DB_USER<\/td>/g" Step4.tpl

    db_password=$(grep -n DB_PASSWORD Step4.tpl |cut -d ":" -f1)
    sed -i "$db_password s/\"password/\"hidden/g" Step4.tpl
    sed -i "s/{\$DB_PASSWORD}/$VTIGER_DB_PASSWORD/g" Step4.tpl
    sed -i "s/db_password.*/db_password\">$VTIGER_DB_PASSWORD<\/td>/g" Step4.tpl

    db_name=$(grep -n DB_NAME} Step4.tpl |cut -d ":" -f1)
    sed -i "$db_name s/text/hidden/g" Step4.tpl
    sed -i "s/{\$DB_NAME}/$VTIGER_DB_DATABASE/g" Step4.tpl
    sed -i "s/db_name.*/db_name\">$VTIGER_DB_DATABASE<\/td>/g" Step4.tpl
   
fi


docker-php-entrypoint apache2-foreground

# Install wizard
