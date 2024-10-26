#!/bin/bash

# Define the ini file
INI_FILE="/usr/local/bin/config.ini"

# Install PHP extension by install-php-extensions
## Install install-php-extensions cli
curl -o /usr/local/bin/install-php-extensions -L https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions
chmod 0755 /usr/local/bin/install-php-extensions

install-php-extensions=$(crudini --get "$INI_FILE" php-extension install-php-extensions)
install-php-extensions=$(echo "$install-php-extensions" | tr ',' ' ')
for extension in $install-php-extensions; do
    echo "Start to install $extension"
    install-php-extensions $extension
done

# Install PHP extension by docker-php-ext-install
docker-php-extensions=$(crudini --get "$INI_FILE" php-extension docker-php-ext-install)
docker-php-extensions=$(echo "$docker-php-extensions" | tr ',' ' ')
for extension in $docker-php-extensions; do
    echo "Start to install $extension"
    docker-php-ext-install $extension
done

# Install PHP extension by pecl
pecl-extensions=$(crudini --get "$INI_FILE" php-extension pecl)
pecl-extensions=$(echo "$pecl-extensions" | tr ',' ' ')
for extension in $pecl-extensions; do
    echo "Start to install $extension"
    echo "no" | pecl install $extension
done