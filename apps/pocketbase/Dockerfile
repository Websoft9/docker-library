ARG POCKETBASE_VERSION=v0.40.5

FROM alpine:3.20

ARG POCKETBASE_VERSION

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="PocketBase packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/pocketbase" \
      org.opencontainers.image.title="pocketbase" \
      org.opencontainers.image.vendor="Websoft9" \
      org.opencontainers.image.version="${POCKETBASE_VERSION}"

RUN apk add --no-cache bash ca-certificates curl unzip wget

RUN set -eux; \
    version="${POCKETBASE_VERSION#v}"; \
    case "$(apk --print-arch)" in \
      x86_64) pb_arch='amd64' ;; \
      aarch64) pb_arch='arm64' ;; \
      armv7) pb_arch='armv7' ;; \
      *) echo "Unsupported architecture: $(apk --print-arch)" >&2; exit 1 ;; \
    esac; \
    wget -O /tmp/pocketbase.zip "https://github.com/pocketbase/pocketbase/releases/download/${POCKETBASE_VERSION}/pocketbase_${version}_linux_${pb_arch}.zip"; \
    unzip /tmp/pocketbase.zip -d /usr/local/bin; \
    chmod +x /usr/local/bin/pocketbase; \
    rm -f /tmp/pocketbase.zip; \
    mkdir -p /pb_data

COPY src/entrypoint.sh /usr/local/bin/entrypoint.sh

RUN chmod +x /usr/local/bin/entrypoint.sh

EXPOSE 8090

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
