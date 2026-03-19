# Moodle Dockerfile based on moodlehq/moodle-php-apache
# Official base image: https://hub.docker.com/r/moodlehq/moodle-php-apache
# Install guide: https://docs.moodle.org/en/Installation_quick_guide

FROM moodlehq/moodle-php-apache:8.3-bullseye

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
    org.opencontainers.image.description="Moodle packaged by Websoft9" \
    org.opencontainers.image.title="Moodle" \
    org.opencontainers.image.vendor="Websoft9 Inc." \
    org.opencontainers.image.version="5.1.3"

ENV MOODLE_VERSION=5.1.3 \
    MOODLE_DATA=/var/moodledata \
    APACHE_DOCUMENT_ROOT=/var/www/html/public

# Install system tools (all Moodle PHP extensions are pre-installed by base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    cron \
    default-mysql-client \
    && rm -rf /var/lib/apt/lists/*

# Enable Apache modules
RUN a2enmod rewrite expires headers

# Create Moodle data directory with correct permissions
RUN mkdir -p ${MOODLE_DATA} \
    && chown -R www-data:www-data ${MOODLE_DATA} \
    && chmod 777 ${MOODLE_DATA}

# Download Moodle source code
# For CI/CD: no proxy needed. For local builds behind a firewall:
#   docker build --network=host --build-arg CURL_PROXY=socks5h://127.0.0.1:1080 ...
ARG CURL_PROXY=
WORKDIR /var/www/html
RUN curl ${CURL_PROXY:+--proxy "$CURL_PROXY"} -fsSL -o /tmp/moodle.zip \
    "https://packaging.moodle.org/stable501/moodle-${MOODLE_VERSION}.zip" \
    && unzip -q /tmp/moodle.zip -d /tmp/moodle_src \
    && cp -a /tmp/moodle_src/moodle/. /var/www/html/ \
    && rm -rf /tmp/moodle.zip /tmp/moodle_src \
    && chown -R www-data:www-data /var/www/html

# Moodle scheduled task (cron)
RUN echo "* * * * * www-data /usr/local/bin/php /var/www/html/admin/cli/cron.php >/dev/null 2>&1" \
    >> /etc/crontab

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["apache2-foreground"]
