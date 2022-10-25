ARG JDK_VERSION=${JDK_VERSION}

FROM openjdk:${JDK_VERSION}-bullseye

LABEL maintainer="help@websoft9.com"
LABEL version="${JDK_VERSION}"
LABEL description="JAVA runtime for ${JDK_VERSION}"
  
RUN apt update && apt install -y --no-install-recommends lsb-release  wget openssl git

RUN mkdir -p /data/apps;

COPY --from=tomcat /usr/local/tomcat /data/apps/tomcat

# install supervisord
RUN apt install -y supervisor

