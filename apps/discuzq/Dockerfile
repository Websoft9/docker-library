# image:https://hub.docker.com/r/websoft9dev/discuzq
# DiscuzQ image is search from TecentCloud image service center publicimage

FROM ccr.ccs.tencentyun.com/discuzq/dzq:latest

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="DiscuzQ packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/discuzq" \
      org.opencontainers.image.title="DiscuzQ" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="latest"

ENV DISCUZQ_MYSQL_HOST=mysql
ENV DISCUZQ_MYSQL_USER=discuzq
ENV DISCUZQ_MYSQL_PASSWORD=discuzq
ENV DISCUZQ_MYSQL_DATABASE=discuzq
ENV DISCUZQ_SITENAME=DiscuzQ

COPY cmd.sh /tmp
RUN chmod +x /tmp/cmd.sh

CMD ["/tmp/cmd.sh"]
