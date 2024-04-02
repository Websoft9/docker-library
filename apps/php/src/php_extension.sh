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
declare -A pecl_extensions_inputs
pecl_extensions_inputs=(
  [mongodb]="no"
  [apcu]="no"
  [redis]="no"
  [memcached]="no"
  [mcrypt]="mcrypt"
  [imagick]="imagick"
)

pecl install xmlrpc-1.0.0RC3 || echo "Failed to install xmlrpc"

for ext in "${!pecl_extensions_inputs[@]}"; do
  input=${pecl_extensions_inputs[$ext]}
  echo "$input" | pecl install "$ext" || echo "Failed to install $ext"
done

# Set recommended PHP.ini settings
# See https://secure.php.net/manual/en/opcache.installation.php
settings=(
    'opcache.memory_consumption=128'
    'opcache.interned_strings_buffer=8'
    'opcache.max_accelerated_files=4000'
    'opcache.revalidate_freq=60'
    'opcache.fast_shutdown=1'
)

# Use a loop to write/append each setting to the file
for setting in "${settings[@]}"; do
    echo "$setting" >> /usr/local/etc/php/conf.d/opcache-recommended.ini
done

# Set custom PHP settings
configurations=(
    "file_uploads = On"
    "max_input_time = 800"
    "max_execution_time = 300"
    "memory_limit = 600M"
    "upload_max_filesize = 900M"
    "post_max_size = 900M"
    "max_file_uploads = 200"
    "error_reporting = E_ALL & ~E_DEPRECATED & ~E_STRICT"
)

for config in "${configurations[@]}"; do
    echo "$config" >> /usr/local/etc/php/conf.d/php_extra.ini
done
