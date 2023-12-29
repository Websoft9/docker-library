ARG JDK_VERSION=${JDK_VERSION}
FROM openjdk:${JDK_VERSION}-buster

ARG JDK_VERSION=${JDK_VERSION}

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="JAVA runtime by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/runtime" \
      org.opencontainers.image.title="java" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="${JDK_VERSION}"
  
RUN apt update && apt install -y --no-install-recommends lsb-release  wget openssl git

RUN mkdir -p /data/apps/jenkins

RUN if [ ${JDK_VERSION} = 17 ]; \
    then \
        echo "start downloading jenkins"; \
        cd /data/apps/jenkins && wget https://mirrors.jenkins.io/war-stable/latest/jenkins.war ;\
    else  \
        echo "do nothing"; \
    fi \
    && echo "install jenkins suucess"
          
# install supervisord
RUN apt install -y supervisor
