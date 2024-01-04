FROM php:7.2-apache

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Application packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/discuzq" \
      org.opencontainers.image.title="Discuz! Q" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="v4.1.3"

ARG DZQ_VERSION='v4.1.3'

ENV INSTALL_DIR /var/www/html

ADD https://github.com/mlocati/docker-php-extension-installer/releases/latest/download/install-php-extensions /usr/local/bin/

COPY --from=composer /usr/bin/composer /usr/bin/composer

RUN apt-get update && apt-get upgrade -y; \
    apt-get install -y wget unzip zip zlib1g-dev libpng-dev libjpeg-dev libfreetype6-dev libwebp-dev libzip-dev libc-client-dev imagemagick libkrb5-dev ghostscript ; \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl ; \
    docker-php-ext-configure gd --with-freetype --with-jpeg=/usr --with-webp ; \
    docker-php-ext-install -j "$(nproc)"  imap gd zip bcmath opcache exif mysqli ; \
    rm -rf /var/lib/apt/lists/* ; \
    mv "$PHP_INI_DIR/php.ini-production" "$PHP_INI_DIR/php.ini"

# this step if only for install php extension alternative, it need 5min for compile
# RUN chmod +x /usr/local/bin/install-php-extensions && install-php-extensions gd zip

# Download DiscuzQ and build
RUN git clone --depth=1 https://gitee.com/Discuz/Discuz-Q.git; \
    cd Discuz-Q/resources/frame && npm install && npm run build; \
    chmod -R 777 /var/www/html

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
	} > /usr/local/etc/php/conf.d/discuzq-recommended.ini

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