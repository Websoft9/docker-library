ARG JDK_VERSION=${JDK_VERSION}

FROM openjdk:${JDK_VERSION}-buster

LABEL maintainer="help@websoft9.com"
LABEL version="${JDK_VERSION}"
LABEL description="JAVA runtime for ${JDK_VERSION}"
  
RUN apt update && apt install -y --no-install-recommends lsb-release  wget openssl git

RUN mkdir -p /data/apps/jenkins
RUN cd /data/apps/jenkins && wget https://mirrors.jenkins.io/war-stable/latest/jenkins.war

# install supervisord
RUN apt install -y supervisor

