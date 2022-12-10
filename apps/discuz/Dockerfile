FROM joomla:php7.4-apache

LABEL maintainer="help@websoft9.com"
LABEL version="Discuz_X3.4_SC_UTF8_20220810"
LABEL description="Discuz"

ENV DISCUZ_DB_HOST=mysql
ENV DISCUZ_DB_USER=discuz
ENV DISCUZ_DB_PASSWORD=discuz
ENV DISCUZ_DB_DATABASE=discuz

RUN apt-get update && apt-get upgrade -y && apt install unzip zip -y; \
    rm -rf /var/lib/apt/lists/* ; 

COPY  ./src/Discuz_X3.4_SC_UTF8_20220811.zip /tmp

COPY entrypoint.sh /entrypoint.sh


RUN set -ex; \
    cd /tmp && mkdir /usr/src/discuz; \
    unzip Discuz_* -d /usr/src/discuz; \
    chown -R www-data:www-data /usr/src/discuz

RUN  chmod +x /entrypoint.sh
