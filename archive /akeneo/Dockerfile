# refer to: https://github.com/chandrantwins/akeneo-docker/blob/master/Dockerfile
# akeneo version: https://packagist.org/packages/akeneo/pim-community-standard
# upgrade to: 7.0.23

FROM akeneo/pim-php-dev:8.1

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Akeneo powered by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/akeneo" \
      org.opencontainers.image.title="Akeneo" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="7.0.23"

ENV AKENEO_MYSQL_HOST=mysql
ENV AKENEO_MYSQL_PORT=3306
ENV AKENEO_MYSQL_USER=akeneo
ENV AKENEO_MYSQL_PASSWORD=akeneo
ENV AKENEO_MYSQL_DATABASE=akeneo
ENV AKENEO_ADMIN_USER=admin 
ENV AKENEO_ADMIN_PASSWORD=admin


RUN apt update -y && apt install apache2 unzip make -y
RUN apt clean && rm -rf /var/lib/apt/lists/*
RUN a2enmod rewrite proxy_fcgi actions alias expires headers ssl
ADD 000-default.conf /etc/apache2/sites-available/000-default.conf
ADD entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && \
    sed -i "s#memory_limit = .*.M#memory_limit = 1024M#g"  /etc/php/8.1/fpm/php.ini && \
    sed -i "s#listen = .*#listen = /run/php/php8.1-fpm.sock#g"  /etc/php/8.1/fpm/pool.d/www.conf
    
ENTRYPOINT ["/entrypoint.sh"]


RUN curl -sL https://deb.nodesource.com/setup_16.x -o nodesource_setup.sh
RUN bash nodesource_setup.sh && apt install nodejs && npm install -g yarn
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer
RUN rm -rf /var/www/html/*
RUN COMPOSER_MEMORY_LIMIT=-1 && \
    composer config -g repo.packagist composer https://mirrors.aliyun.com/composer/ && \
    composer create-project akeneo/pim-community-standard /var/www/html

WORKDIR /var/www/html
RUN chown -R www-data:www-data /var/www/html
RUN yarn install
RUN PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1 yarnpkg packages:build

EXPOSE 80

CMD ["/usr/sbin/apache2ctl", "-D", "FOREGROUND"]