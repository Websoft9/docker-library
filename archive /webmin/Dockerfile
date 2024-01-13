# Use the latest Ubuntu image as a parent
FROM ubuntu:focal

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Webmin packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/webmin" \
      org.opencontainers.image.title="Webmin" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="latest"

ENV DEBIAN_FRONTEND=noninteractive TZ=Europe/Amsterdam 
ENV WEBMIN_PASSWORD=admin123456

# Initial updates and install core utilities
RUN apt-get update -qq -y && \
    apt-get upgrade -y && \
    apt-get install -y \
       wget \
       curl \
       apt-transport-https \
       lsb-release \
       ca-certificates \
       gnupg2 \
       software-properties-common \
       locales \
       cron    
RUN dpkg-reconfigure locales

# Install Webmin
RUN echo "start build" && \
    echo "Acquire::GzipIndexes \"false\"; Acquire::CompressionTypes::Order:: \"gz\";" >/etc/apt/apt.conf.d/docker-gzip-indexes && \
    update-locale LANG=C.UTF-8 && \
    echo deb https://download.webmin.com/download/repository sarge contrib >> /etc/apt/sources.list && \
    wget http://www.webmin.com/jcameron-key.asc && \
    apt-key add jcameron-key.asc && \
    apt-get update && \
    apt-get install -y webmin && \
    apt-get clean

EXPOSE 10000
ENV LC_ALL C.UTF-8

WORKDIR /home

ADD entrypoint.sh /home/

RUN chmod 755 /home/entrypoint.sh

CMD /home/entrypoint.sh
