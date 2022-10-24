ARG JDK_VERSION=${JDK_VERSION}

FROM openjdk:${JDK_VERSION}

LABEL maintainer="help@websoft9.com"
LABEL version="${JDK_VERSION}"
LABEL description="JAVA runtime for ${JDK_VERSION}"
  
RUN apt-get update && apt-get install -y --no-install-recommends lsb-release  wget openssl git

RUN mkdir -p /data/apps;

COPY --from=tomcat:${TOMCAT_VERSION} /usr/local/tomcat /data/apps

# install supervisord
RUN apt install -y supervisor
