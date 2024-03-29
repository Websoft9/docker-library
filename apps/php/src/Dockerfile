ARG PHP_VERSION=${PHP_VERSION}
ARG GIT_URL=${GIT_URL}

FROM php:${PHP_VERSION}-apache

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${PHP_VERSION}"

COPY --from=composer/composer /usr/bin/composer /usr/bin/composer
RUN apt-get update && apt-get install -y --no-install-recommends git

# Git clone and php composer, and add your commands

RUN if [ -z "$GIT_URL" ]; then echo "GIT_URL not provided" && exit 1; fi && \
    git clone "$GIT_URL" . ; \
    ##################### customer commands start ##########################

    #composer
    if not have index.php, echo '<?php echo "It seam not have index.php at root directory"; ?>' > index.php

    ##################### customer commands end ##########################


# Install os common package for more PHP applications
RUN apt-get update && apt-get install -y --no-install-recommends \

# Install php module for more PHP applications
RUN docker-php-ext-configure gd \
		--with-freetype \
		--with-jpeg=/usr \
		--with-webp \
	|| true; \
	\
	docker-php-ext-install -j "$(nproc)" \
		bcmath \
		exif \
		intl \
		gd \
		pcntl \
		opcache \
		pdo_mysql \
		pdo_pgsql \
                pgsql \
                mysqli \
                soap \
                snmp \
                tidy \
                gmp \
                mysqli \
                bz2 \
		zip \
		ldap || true

# Config and install odbc and imap
RUN { \
      echo '# https://github.com/docker-library/php/issues/103#issuecomment-271413933'; \
      echo 'AC_DEFUN([PHP_ALWAYS_SHARED],[])dnl'; \
      echo; \
      cat /usr/src/php/ext/odbc/config.m4; \
    } > temp.m4; \
    mv temp.m4 /usr/src/php/ext/odbc/config.m4; \
    docker-php-ext-configure odbc --with-unixODBC=shared,/usr; \
    docker-php-ext-install odbc; \
    docker-php-ext-configure imap --with-kerberos --with-imap-ssl; \
    docker-php-ext-install imap

# Install pecl packge
RUN pecl install mongodb; \
    pecl install xmlrpc-1.0.0RC3; \
    echo "no" | pecl install apcu; \
    echo "no" | pecl install redis; \
    echo "no" | pecl install memcached; \
    echo "mcrypt" | pecl install mcrypt; \
    echo "imagick" | pecl install imagick

# Set recommended PHP.ini settings
# See https://secure.php.net/manual/en/opcache.installation.php
RUN { \
		echo 'opcache.memory_consumption=128'; \
		echo 'opcache.interned_strings_buffer=8'; \
		echo 'opcache.max_accelerated_files=4000'; \
		echo 'opcache.revalidate_freq=60'; \
		echo 'opcache.fast_shutdown=1'; \
	} > /usr/local/etc/php/conf.d/opcache-recommended.ini