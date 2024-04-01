#!/bin/bash

PATH=/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin:/usr/local/sbin:~/bin
export PATH

####################---------- Description ----------- ###################
# php image is based on debian, so we can use apt-get to install packages
# this package is os level packages, which is required by php or php extension
# We should continue when install a package failed, so we use || to continue

# You can delete any package you don't need
tools_apt="git acl mosh curl wget gnupg2 ca-certificates  openssl unzip bzip2 at tree vim screen pwgen htop imagemagick goaccess jq net-tools mlocate chrony gnupg dirmngr ghostscript unixodbc-dev libfreetype6-dev libjpeg-dev libpng-dev libpq-dev libwebp-dev libzip-dev libcurl4-openssl-dev libicu-dev libldap2-dev libmemcached-dev libsnmp-dev libtidy-dev libmcrypt-dev libgmp-dev libmagickwand-dev libmagickcore-dev libc-client-dev libkrb5-dev libc-client-dev libbz2-dev libxml2-dev"

apt-get update -y 1>/dev/null 2>&1
for package in $tools_apt; do 
    echo "Start to install $package"
    apt-get install $package -y > /dev/null  || echo "$package failed to install"                     
done
