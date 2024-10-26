# 使用 ARG 来读取环境变量
ARG PHP_VERSION

FROM php:${PHP_VERSION}

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PHP runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/php" \
      org.opencontainers.image.title="php" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${PHP_VERSION}"

# Set environment variables to avoid interactive configuration
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary tools, including crudini
RUN apt-get update && \
    apt-get install -y \
    crudini \
    && apt-get clean

COPY src/extensions.ini /usr/local/bin/config.ini
COPY src/apt_install.sh /usr/local/bin/apt_install.sh
COPY src/php_install.sh /usr/local/bin/php_install.sh

RUN chmod +x /usr/local/bin/apt_install.sh
RUN chmod +x /usr/local/bin/php_install.sh

RUN /usr/local/bin/apt_install.sh
RUN /usr/local/bin/php_install.sh