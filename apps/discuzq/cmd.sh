#!/bin/bash

# create by websoft9
# Replace DB connetion
if [[ -f /var/www/discuz/config/config.php ]]; then
   echo "Initialization has been completed before this time!"
else
    
   sed -i "s/forumTitle.*/forumTitle\" value=\"$DISCUZQ_SITENAME\">/g" /var/www/discuz/resources/views/install/install.blade.php
   sed -i "s/mysqlHost.*/mysqlHost\" value=\"$DISCUZQ_MYSQL_HOST\">/g" /var/www/discuz/resources/views/install/install.blade.php
   sed -i "s/mysqlDatabase.*/mysqlDatabase\" value=\"$DISCUZQ_MYSQL_DATABASE\">/g" /var/www/discuz/resources/views/install/install.blade.php
   sed -i "s/mysqlUsername.*/mysqlUsername\" value=\"$DISCUZQ_MYSQL_DATABASE\">/g" /var/www/discuz/resources/views/install/install.blade.php
   sed -i "s/mysqlPassword.*/mysqlPassword\" value=\"$DISCUZQ_MYSQL_PASSWORD\">/g" /var/www/discuz/resources/views/install/install.blade.php
   sed -i "s/tablePrefix.*/tablePrefix\" value=\"discuzq\">/g" /var/www/discuz/resources/views/install/install.blade.php
fi


# CMD from ccr.ccs.tencentyun.com/discuzq/dzq:latest
/usr/sbin/supervisord -c /etc/supervisord.conf

# Install wizard
