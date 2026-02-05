# Moodle Dockerfile based on official php:apache
# Reference: https://docs.moodle.org/501/en/Installation_quick_guide

FROM php:8.2-apache

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Moodle packaged by Websoft9" \
      org.opencontainers.image.source="https://packaging.moodle.org/stable501/moodle-5.1.1.zip" \
      org.opencontainers.image.title="Moodle" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="5.1.1"
      
# Moodle version
ENV MOODLE_VERSION=5.1.1 \
    MOODLE_DATA=/var/moodledata

# Install system dependencies and PHP extensions required by Moodle
RUN apt-get update && apt-get install -y \
    # Basic tools
    wget \
    unzip \
    git \
    cron \
    # Libraries for PHP extensions
    libicu-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    libfreetype6-dev \
    libxml2-dev \
    libzip-dev \
    libldap2-dev \
    libpq-dev \
    libonig-dev \
    libxslt1-dev \
    libcurl4-openssl-dev \
    # Database clients
    default-mysql-client \
    postgresql-client \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Configure and install PHP extensions required by Moodle
# GD extension
RUN docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd

# Install other extensions
RUN docker-php-ext-install -j$(nproc) \
        intl \
        mysqli \
        pgsql \
        pdo_mysql \
        pdo_pgsql \
        opcache \
        zip \
        soap \
        mbstring \
        exif

# LDAP extension (configure separately to avoid path issues)
RUN docker-php-ext-configure ldap \
    && docker-php-ext-install ldap

# Install additional recommended PHP extensions
RUN pecl install redis \
    && docker-php-ext-enable redis

# Configure PHP settings for Moodle
RUN { \
        echo 'file_uploads = On'; \
        echo 'memory_limit = 512M'; \
        echo 'upload_max_filesize = 512M'; \
        echo 'post_max_size = 512M'; \
        echo 'max_execution_time = 600'; \
        echo 'max_input_vars = 5000'; \
        echo 'max_input_time = 600'; \
        echo 'session.save_handler = files'; \
        echo 'session.auto_start = 0'; \
        echo 'session.gc_maxlifetime = 1440'; \
        echo 'zend.exception_ignore_args = On'; \
    } > /usr/local/etc/php/conf.d/moodle.ini

# Configure OPcache for performance
RUN { \
        echo 'opcache.enable = 1'; \
        echo 'opcache.memory_consumption = 128'; \
        echo 'opcache.interned_strings_buffer = 8'; \
        echo 'opcache.max_accelerated_files = 4000'; \
        echo 'opcache.revalidate_freq = 60'; \
        echo 'opcache.fast_shutdown = 1'; \
    } > /usr/local/etc/php/conf.d/opcache-recommended.ini

# Enable Apache modules
RUN a2enmod rewrite expires headers ssl

# Configure Apache DocumentRoot to use /public directory (Moodle 5.0+ requirement)
RUN sed -i 's|DocumentRoot /var/www/html|DocumentRoot /var/www/html/public|g' /etc/apache2/sites-available/000-default.conf \
    && sed -i 's|<Directory /var/www/>|<Directory /var/www/html/>\n    Options Indexes FollowSymLinks\n    AllowOverride All\n    Require all granted\n</Directory>\n<Directory /var/www/html/public/>|g' /etc/apache2/apache2.conf

# Create moodledata directory with proper permissions
RUN mkdir -p ${MOODLE_DATA} \
    && chown -R www-data:www-data ${MOODLE_DATA} \
    && chmod -R 0777 ${MOODLE_DATA}

# Download and extract Moodle
WORKDIR /var/www/html
RUN wget -O moodle.zip "https://packaging.moodle.org/stable501/moodle-${MOODLE_VERSION}.zip" \
    && unzip -q moodle.zip \
    && mv moodle/* moodle/.??* . 2>/dev/null || true \
    && rmdir moodle \
    && rm moodle.zip \
    && chown -R www-data:www-data /var/www/html \
    && chmod -R 0755 /var/www/html

# Setup cron job for Moodle
RUN echo "* * * * * www-data /usr/local/bin/php /var/www/html/admin/cli/cron.php >/dev/null" >> /etc/crontab

# Create entrypoint script
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

EXPOSE 80

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["apache2-foreground"]
