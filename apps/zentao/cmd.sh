#!/bin/bash
# customrized cmd powered by Websoft

sed -i "s/dbHost : '127.0.0.1'/dbHost : '$MYSQL_HOST'/g" /var/www/zentaopms/module/install/control.php
sed -i "s/dbName : 'zentao'/dbName : '$MYSQL_DB'/g" /var/www/zentaopms/module/install/control.php
sed -i "s/dbPassword : ''/dbPassword : '$MYSQL_PASSWORD'/g" /var/www/zentaopms/module/install/control.php

bash /.docker_init.sh
