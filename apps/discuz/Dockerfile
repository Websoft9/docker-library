# update time: 202312161657

FROM joomla:php7.4-apache

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Discuz packaged by Websoft9" \
      org.opencontainers.image.source="Discuz_X3.5_SC_UTF8_20231001" \
      org.opencontainers.image.title="Discuz" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="v3.5.0"

ENV DISCUZ_DB_HOST=mysql
ENV DISCUZ_DB_USER=discuz
ENV DISCUZ_DB_PASSWORD=discuz
ENV DISCUZ_DB_DATABASE=discuz

RUN apt-get update && apt-get upgrade -y && apt install unzip zip -y; \
    rm -rf /var/lib/apt/lists/* 

COPY  ./src/Discuz_* /tmp

COPY entrypoint.sh /entrypoint.sh


RUN set -ex; \
    cd /tmp && mkdir /usr/src/discuz; \
    unzip Discuz_* -d /usr/src/discuz; \
    chown -R www-data:www-data /usr/src/discuz

RUN  chmod +x /entrypoint.sh
