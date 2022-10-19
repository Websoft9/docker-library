#! /bin/bash

if [[ -f /var/www/html/config/config_global_default.php ]]; then
    echo "Initialization has been completed before this time!"
else
    sed -i "s/127.0.0.1/db/g" /usr/src/discuz/upload/config/config_global_default.php
    sed -i "s/ultrax/$DISCUZ_DB_DATABASE/g" /usr/src/discuz/upload/config/config_global_default.php
    sed -i "34{s/=.*/= '$DISCUZ_DB_PASSWORD';/}"  /usr/src/discuz/upload/config/config_global_default.php
fi

/entrypoint.sh apache2-foreground
