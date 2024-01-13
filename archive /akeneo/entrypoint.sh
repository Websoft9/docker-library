#!/bin/bash

localexist=/var/www/html/.env.local
if [ ! -e "$localexist" ]; then

    echo "file:.env.local isn't exist"
    
    # replace Akeneo env
    cp /var/www/html/.env  /var/www/html/.env.local
    sed -i "s/W9_DATABASE_HOST=.*/W9_DATABASE_HOST=$AKENEO_MYSQL_HOST/g"  /var/www/html/.env.local
    sed -i "s/W9_DATABASE_PORT=.*/W9_DATABASE_PORT=$AKENEO_MYSQL_PORT/g"  /var/www/html/.env.local
    sed -i "s/W9_DATABASE_NAME=.*/W9_DATABASE_NAME=$AKENEO_MYSQL_DATABASE/g"  /var/www/html/.env.local
    sed -i "s/W9_DATABASE_USER=.*/W9_DATABASE_USER=$AKENEO_MYSQL_USER/g"  /var/www/html/.env.local
    sed -i "s/W9_DATABASE_PASSWORD=.*/W9_DATABASE_PASSWORD=$AKENEO_MYSQL_PASSWORD/g"  /var/www/html/.env.local

    # to do: make prod  
    cd /var/www/html && NO_DOCKER=true make prod 
    chown -R www-data:www-data /var/www/html

    # create administrator credential
    bin/console pim:user:create $AKENEO_ADMIN_USER $AKENEO_ADMIN_PASSWORD support@example.com Admin Admin en_US --admin -n --env=prod

    # Add local user
    # Either use the LOCAL_USER_ID if passed in at runtime or
    # fallback

    USER_ID=${LOCAL_USER_ID:-1000}
    usermod -u $USER_ID -o www-data && groupmod -g $USER_ID -o www-data
else
    echo "file:.env.local is exist."
fi

/etc/init.d/php8.1-fpm start
exec "$@"