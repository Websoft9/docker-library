# image: https://hub.docker.com/r/websoft9dev/discuzq

FROM ccr.ccs.tencentyun.com/discuzq/dzq:latest

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Application packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/opencart" \
      org.opencontainers.image.title="OpenCart" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="4.0.1.1"

ENV DISCUZQ_MYSQL_HOST=mysql
ENV DISCUZQ_MYSQL_USER=discuzq
ENV DISCUZQ_MYSQL_PASSWORD=discuzq
ENV DISCUZQ_MYSQL_DATABASE=discuzq
ENV DISCUZQ_SITENAME=DiscuzQ

COPY cmd.sh /tmp
RUN chmod +x /tmp/cmd.sh

CMD ["/tmp/cmd.sh"]
