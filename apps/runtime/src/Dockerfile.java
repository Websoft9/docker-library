ARG JDK_VERSION=${JDK_VERSION}

FROM openjdk:${JDK_VERSION}-buster

LABEL maintainer="help@websoft9.com"
LABEL version="${JDK_VERSION}"
LABEL description="JAVA runtime for ${JDK_VERSION}"
  
RUN apt update && apt install -y  wget 

RUN mkdir -p /data/apps/jenkins

RUN if [ ${JDK_VERSION} == 17 ]; \
    then \
        echo "start downloading jenkins"; \
        cd /data/apps/jenkins && wget https://mirrors.jenkins.io/war-stable/latest/jenkins.war ;\
    else  \
        echo "do nothing"; \
    fi \
    && echo "install jenkins suucess"
          
# install supervisord
RUN apt install -y supervisor
