## This file is for your CI


## Install Linux packages, e.g unzip git
apt update -y && apt install unzip git -y

## Install install-php-extensions cli
curl -o /usr/local/bin/install-php-extensions -L https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions
chmod 0755 /usr/local/bin/install-php-extensions

## Install php extension, e.g Composer, mysqli
install-php-extensions @composer
install-php-extensions mysqli

## create php sample by default
echo "<?php phpinfo(); ?>" > /var/www/html/index.php

## Install WordPress for your reference

# cd /var/www/html 
# curl -O https://wordpress.org/latest.zip
# unzip latest.zip
# mv wordpress/* ./
# chown -R www-data:www-data /var/www/html

