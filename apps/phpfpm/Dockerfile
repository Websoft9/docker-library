ARG PHP_VERSION=5.5-fpm

FROM php:${PHP_VERSION}

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${PHP_VERSION}"

# Set environment variables to avoid interactive configuration
ENV DEBIAN_FRONTEND=noninteractive

# replace apt repository for php7.0/5.6 image
RUN sed -i  's|deb http://deb.debian.org/debian stretch|deb http://archive.debian.org/debian stretch|g' /etc/apt/sources.list || true && \
    sed -i  '/stretch-updates/d' /etc/apt/sources.list || true && \
    sed -i  's|deb http://security.debian.org/debian-security stretch/updates|deb http://archive.debian.org/debian-security stretch/updates|g' /etc/apt/sources.list || true

RUN apt update && apt install -y crudini nginx

COPY src/extensions.ini /usr/local/bin/config.ini
COPY src/apt_install.sh /usr/local/bin/apt_install.sh
COPY src/php_install.sh /usr/local/bin/php_install.sh
COPY src/nginx.conf /etc/nginx/sites-available/default

RUN chmod +x /usr/local/bin/apt_install.sh
RUN chmod +x /usr/local/bin/php_install.sh

RUN /usr/local/bin/apt_install.sh
RUN /usr/local/bin/php_install.sh

RUN apt clean

EXPOSE 80 9000

CMD ["sh", "-c", "service nginx start && php-fpm"]