#!/bin/bash

# Define the ini file
INI_FILE="/usr/local/bin/config.ini"

# Install PHP extension by install-php-extensions
## Install install-php-extensions cli
curl -o /usr/local/bin/install-php-extensions -L https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions
chmod 0755 /usr/local/bin/install-php-extensions
phpExtensions=$(crudini --get "$INI_FILE" php-extension install-php-extensions)
phpExtensions=$(echo "$phpExtensions" | tr ',' ' ')
for extension in $phpExtensions; do
    echo "Start to install $extension by install-php-extensions"
    install-php-extensions $extension
    docker-php-ext-enable $extension
done

# Install PHP extension by docker-php-ext-install
dockerExtensions=$(crudini --get "$INI_FILE" php-extension docker-php-ext-install)
dockerExtensions=$(echo "$dockerExtensions" | tr ',' ' ')
for extension in $dockerExtensions; do
    echo "Start to install $extension  by docker-php-ext-install"
    docker-php-ext-install $extension
    docker-php-ext-enable $extension
done

# Install PHP extension by pecl
peclExtensions=$(crudini --get "$INI_FILE" php-extension pecl)
peclExtensions=$(echo "$peclExtensions" | tr ',' ' ')
for extension in $peclExtensions; do
    echo "Start to install $extension by pecl"
    yes '' | pecl install $extension
    docker-php-ext-enable $extension
done