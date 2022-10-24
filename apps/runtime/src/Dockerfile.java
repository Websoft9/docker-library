ARG PHP_VERSION=${JAVA_VERSION}

FROM openjdk:${JAVA_VERSION}

LABEL maintainer="help@websoft9.com"
LABEL version="${JAVA_VERSION}"
LABEL description="JAVA runtime for ${JAVA_VERSION}"
