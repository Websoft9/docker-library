FROM php:8.3-apache

LABEL maintainer="Websoft9<help@websoft9.com>"
LABEL version="2.4.8"

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
RUN composer config -g http-basic.repo.magento.com 37bb3b989cea3977c859efc7f6a22f74 a5b8ceac57dbeabf0a3a6f4d6301803f
RUN composer create-project --repository-url=https://repo.magento.com/ magento/project-community-edition=2.4.8 /var/www/html

RUN a2enmod expires headers rewrite security2

RUN apt clean

CMD ["/bin/bash", "-c", "bash /usr/local/bin/cmd.sh && apache2-foreground"]