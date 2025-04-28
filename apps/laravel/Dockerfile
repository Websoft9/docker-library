ARG PHP_VERSION=8.3-apache

FROM php:8.3-apache

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="12.0.7"

# Set environment variables to avoid interactive configuration
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y crudini

COPY src/extensions.ini /usr/local/bin/config.ini
COPY src/apt_install.sh /usr/local/bin/apt_install.sh
COPY src/php_install.sh /usr/local/bin/php_install.sh
COPY src/cmd.sh /usr/local/bin/cmd.sh

RUN chmod +x /usr/local/bin/apt_install.sh
RUN chmod +x /usr/local/bin/php_install.sh
RUN chmod +x /usr/local/bin/cmd.sh

RUN /usr/local/bin/apt_install.sh
RUN /usr/local/bin/php_install.sh
RUN composer global require laravel/installer \
    export PATH="$PATH:/root/.composer/vendor/bin" \
    echo 'export PATH="$PATH:/root/.composer/vendor/bin"' >> ~/.bashrc \
    source ~/.bashrc \
    laravel new laravel --force --no-interaction

RUN apt clean

CMD ["/bin/bash", "-c", "bash /usr/local/bin/cmd.sh && php artisan serve --host=0.0.0.0 --port=8000 --no-interaction"]