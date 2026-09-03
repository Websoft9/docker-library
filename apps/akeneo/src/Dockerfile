ARG AKENEO_VERSION=v2026.4

FROM akeneo/pim-php-dev:8.3

ARG AKENEO_VERSION

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Akeneo packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/akeneo" \
      org.opencontainers.image.title="akeneo" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${AKENEO_VERSION}"

ENV APP_ENV=prod \
    COMPOSER_MEMORY_LIMIT=-1 \
    PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1

USER root

RUN mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_18.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends apache2 default-mysql-client gnupg nodejs \
    && npm install -g yarn@1.22.22 \
    && a2enmod rewrite proxy proxy_fcgi actions alias expires headers \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/local/bin/composer

WORKDIR /var/www/html

RUN rm -rf /var/www/html/* \
    && composer create-project --prefer-dist --no-interaction akeneo/pim-community-standard /var/www/html "${AKENEO_VERSION}" \
    && chown -R www-data:www-data /var/www/html

USER www-data

RUN (yarn install || yarn install --network-concurrency 1) \
    && php bin/console cache:warmup --env=prod \
    && php bin/console pim:installer:assets --symlink --clean --env=prod \
    && php bin/console pim:installer:dump-require-paths --env=prod \
    && yarn packages:build \
    && yarn webpack \
    && yarn less \
    && yarn update-extensions

USER root

COPY src/000-default.conf /etc/apache2/sites-available/000-default.conf
COPY src/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh \
    && a2ensite 000-default \
    && mkdir -p /var/www/html/var/file_storage /var/www/html/var/logs /var/www/html/var/cache \
    && chown -R www-data:www-data /var/www/html

EXPOSE 80

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["web"]
