#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

####################---------- Description ----------- ###################
# This script is used to do some things:
# 1. install PHP extensions
# 2. install pecl package
# 3. set recommended PHP.ini settings

# You must confige PHP GD before other PHP extensions which is dependent on GD
docker-php-ext-configure gd --with-freetype --with-jpeg=/usr --with-webp || true

# Install PHP extensions
extensions=(
  bcmath
  exif
  intl
  gd
  pcntl
  opcache
  pdo_mysql
  pdo_pgsql
  pgsql
  mysqli
  soap
  snmp
  tidy
  gmp
  bz2
  zip
  ldap
)

for ext in "${extensions[@]}"; do
  docker-php-ext-install -j "$(nproc)" "$ext" || echo "Failed to install $ext"
done

# Install special extensions
declare -A special_extensions
special_extensions=(
  [odbc]="--with-unixODBC=shared,/usr"
  [imap]="--with-kerberos --with-imap-ssl"
)

# Config and install odbc
echo '# https://github.com/docker-library/php/issues/103#issuecomment-271413933' > temp.m4
echo 'AC_DEFUN([PHP_ALWAYS_SHARED],[])dnl' >> temp.m4
cat /usr/src/php/ext/odbc/config.m4 >> temp.m4
mv temp.m4 /usr/src/php/ext/odbc/config.m4

for ext in "${!special_extensions[@]}"; do
  # Configure the extension
  docker-php-ext-configure "$ext" ${special_extensions[$ext]} || echo "Failed to configure $ext"
  # Install the extension
  docker-php-ext-install "$ext" || echo "Failed to install $ext"
done

# Install pecl packge
pecl install xmlrpc-1.0.0RC3 || echo "Failed to install xmlrpc"
echo "no" | pecl install mongodb || echo "Failed to install mongodb"
echo "no" | pecl install apcu || echo "Failed to install apcu"
echo "no" | pecl install redis || echo "Failed to install redis"
echo "no" | pecl install memcached || echo "Failed to install memcached"
echo "no" | pecl install mcrypt || echo "Failed to install mcrypt"
echo "no" | pecl install imagick || echo "Failed to install imagick"
