# docs: https://community.vtiger.com/help/vtigercrm/administrators/installation.html
# image: https://hub.docker.com/r/websoft9dev/vtiger
# refer: https://github.com/mohsentm/vtiger-docker/blob/master/Dockerfile

FROM php:7.2-apache

LABEL maintainer="help@websoft9.com"
LABEL version="7.4.0"
LABEL description="Vtiger CRM"

ENV INSTALL_DIR /var/www/html

RUN apt-get update && apt-get upgrade -y; \
    apt-get install -y --no-install-recommends wget zip libc-client-dev libkrb5-dev ghostscript ; \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl ; \
    docker-php-ext-install -j "$(nproc)"  imap bcmath opcache exif mysqli ; \
    rm -rf /var/lib/apt/lists/* ; \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

RUN version='7.4.0'; \
    curl -o vtigercrm.tar.gz -fL "https://sourceforge.net/projects/vtigercrm/files/vtiger%20CRM%20$version/Core%20Product/vtigercrm$version.tar.gz"; \
    tar -xzf vtigercrm.tar.gz; \
    cp -r vtigercrm/* $INSTALL_DIR; \
    rm -rf vtigercrm.tar.gz vtigercrm;\
    chmod -R 777 $INSTALL_DIR

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
	} > /usr/local/etc/php/conf.d/vtiger-recommended.ini

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
