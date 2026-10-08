ARG PHP_VERSION=8.2-fpm

FROM php:${PHP_VERSION}

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${PHP_VERSION}"

# Set environment variables to avoid interactive configuration
ENV DEBIAN_FRONTEND=noninteractive

# replace apt repository for php5.6/7.0-8.0 image
RUN sed -i  '/stretch-updates/d' /etc/apt/sources.list || true && \
    sed -i  '/buster-updates/d' /etc/apt/sources.list || true && \
    sed -i  '/bullseye-updates/d' /etc/apt/sources.list || true && \
    sed -i  '/debian-security/d' /etc/apt/sources.list || true && \
    sed -i  's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list || true

# replace apt repository for php8.1-8.3 image
RUN if [ ! -f /etc/apt/sources.list ]; then \
      rm -rf /etc/apt/sources.list.d/ && \
      echo 'deb http://deb.debian.org/debian trixie main contrib non-free' > /etc/apt/sources.list && \
      echo 'deb http://mirrors.aliyun.com/debian trixie main contrib non-free' >> /etc/apt/sources.list ; \
    fi

RUN apt-get update -oAcquire::AllowInsecureRepositories=true && \
    apt-get install -y --allow-unauthenticated gnupg && \
    apt-get install -y --allow-unauthenticated debian-archive-keyring && \
    apt-key update || true && \
    apt-get update

RUN apt install -y crudini apache2 supervisor
RUN rm -f /var/www/html/index.html && a2enmod proxy_fcgi
COPY src/extensions.ini /usr/local/bin/config.ini
COPY src/apt_install.sh /usr/local/bin/apt_install.sh
COPY src/php_install.sh /usr/local/bin/php_install.sh
COPY src/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY src/supervisord.conf /etc/supervisor/conf.d/supervisord.conf
COPY src/000-default.conf /etc/apache2/sites-available/000-default.conf

RUN chmod +x /usr/local/bin/apt_install.sh /usr/local/bin/php_install.sh /usr/local/bin/entrypoint.sh

RUN /usr/local/bin/apt_install.sh
RUN /usr/local/bin/php_install.sh

RUN apt clean

EXPOSE 80 9000

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]