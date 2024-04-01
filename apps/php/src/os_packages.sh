####---------- Description ---- ###################
###
###

# You can delete any package you don't need
tools_apt="git acl mosh curl gnupg2 ca-certificates wget openssl unzip bzip2 at tree vim screen pwgen htop imagemagick goaccess jq net-tools mlocate chrony gnupg dirmngr ghostscript unixodbc-dev libfreetype6-dev libjpeg-dev libpng-dev libpq-dev libwebp-dev libzip-dev libcurl4-openssl-dev libicu-dev libldap2-dev libmemcached-dev libsnmp-dev libtidy-dev libmcrypt-dev libgmp-dev libmagickwand-dev libmagickcore-dev libc-client-dev libkrb5-dev libc-client-dev libbz2-dev libxml2-dev"

sudo apt-get update -y 1>/dev/null 2>&1
for package in $tools_apt; do 
    echo "Start to install $package"
    sudo apt-get install $package -y > /dev/null
    if [ $? -ne 0 ]; then
        exit 1
    fi                        
done
