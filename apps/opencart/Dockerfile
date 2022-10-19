FROM php:8.1-apache

LABEL maintainer="help@websoft9.com"
LABEL version="4.0.1.1"
LABEL description="OpenCart"

ARG OC_VERSION='4.0.1.1'

ENV INSTALL_DIR /var/www/html

ADD https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions /usr/local/bin/

RUN apt-get update && apt-get upgrade -y; \
    apt-get install -y --no-install-recommends wget unzip zip zlib1g-dev libpng-dev libzip-dev libc-client-dev libkrb5-dev ghostscript ; \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl ; \
    docker-php-ext-install -j "$(nproc)"  imap gd zip bcmath opcache exif mysqli ; \
    rm -rf /var/lib/apt/lists/* ; \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# this step if only for install php extension alternative, it need 5min for compile
# RUN chmod +x /usr/local/bin/install-php-extensions && install-php-extensions gd zip

# Opencart Dashbord need mv storage folder to /var/www, so chmod before
RUN curl -o opencart.zip -fL "https://github.com/opencart/opencart/releases/download/$OC_VERSION/opencart-$OC_VERSION.zip"; \
    unzip opencart.zip -d opencart; \
    cp -r opencart/upload/* $INSTALL_DIR; \
    rm -rf opencart.zip opencart;\
    mv $INSTALL_DIR/config-dist.php $INSTALL_DIR/config.php ; \
    mv $INSTALL_DIR/admin/config-dist.php $INSTALL_DIR/admin/config.php ; \
    chmod -R 777 /var/www

RUN sed -i "s/Options Indexes FollowSymLinks/Options FollowSymLinks/" /etc/apache2/apache2.conf

RUN { \
	echo 'error_reporting = E_ERROR & ~E_NOTICE & ~E_STRICT & ~E_DEPRECATED'; \
	echo 'log_errors = Off'; \
	echo 'display_errors = Off'; \
	echo 'short_open_tag = Off'; \
	echo 'max_execution_time = 300'; \
	echo 'memory_limit = 600M'; \
	echo 'max_input_time = 800'; \
	echo 'post_max_size = 900M'; \
	echo 'upload_max_filesize = 900M'; \
	echo 'max_file_uploads = 200'; \
	} > /usr/local/etc/php/conf.d/opencart-recommended.ini

RUN { \
        echo 'opcache.memory_consumption=128'; \
        echo 'opcache.interned_strings_buffer=8'; \
        echo 'opcache.max_accelerated_files=4000'; \
        echo 'opcache.revalidate_freq=60'; \
        echo 'opcache.fast_shutdown=1'; \
        echo 'opcache.enable_cli=1'; \
} > /usr/local/etc/php/conf.d/opcache-recommended.ini

VOLUME ["$INSTALL_DIR"]

WORKDIR $INSTALL_DIR
