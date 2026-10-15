FROM openjdk:11-jre as build

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Cmak packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/cmak" \
      org.opencontainers.image.title="Cmak" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="3.0.0.5"

ARG CMAK_VERSION="3.0.0.5"

RUN curl -L https://github.com/yahoo/CMAK/releases/download/${CMAK_VERSION}/cmak-${CMAK_VERSION}.zip -o /tmp/cmak.zip \
    && unzip /tmp/cmak.zip -d / \
    && ln -s /cmak-$CMAK_VERSION /cmak \
    && rm -rf /tmp/cmak.zip

FROM openjdk:11-jre-slim
MAINTAINER Hleb Albau <hleb.albau@gmail.com>

COPY --from=build /cmak /cmak

VOLUME /cmak/conf

ENV JAVA_OPTS=-XX:MaxRAMPercentage=80

WORKDIR /cmak

RUN sed -i 's/\/dev\/random/\/dev\/.\/urandom/g' /usr/local/openjdk-11/conf/security/java.security
ENTRYPOINT ["/cmak/bin/cmak", "-Dpidfile.path=/dev/null", "-Dapplication.home=/cmak", ""]

