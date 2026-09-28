ARG DSH_VERSION=0.1.7-rc.2

FROM node:22-slim

ARG DSH_VERSION

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="DeepSeek Harness packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/dsh" \
      org.opencontainers.image.title="dsh" \
      org.opencontainers.image.vendor="Websoft9" \
      org.opencontainers.image.version="${DSH_VERSION}"

ENV DSH_HOME=/var/lib/dsh \
    DSH_WORKSPACE=/workspace \
    HOME=/var/lib/dsh \
    DSH_INTERNAL_PORT=3081 \
    DSH_FORCE_LOOPBACK_UI=true \
    NODE_ENV=production \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false

RUN apt-get update \
    && apt-get install -y --no-install-recommends bash ca-certificates curl git nginx-light openssh-client procps ripgrep \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @deepseek-ai/dsh@${DSH_VERSION} \
    && node -e "const fs=require('fs'); const p='/usr/local/lib/node_modules/@deepseek-ai/dsh/node_modules/@deepseek-ai/dsh-client-connection/lib/client.js'; let s=fs.readFileSync(p,'utf8'); const old='isLoopback: transport?.ownsHost === true || pageLocation === void 0 || isLoopbackHostname(pageLocation.hostname),'; const rep='isLoopback: transport?.ownsHost === true || pageLocation === void 0 || isLoopbackHostname(pageLocation.hostname) || (typeof window !== \'undefined\' && window.__DSH_LOCAL_APP__ === true),'; if(!s.includes(old)) throw new Error('dsh-client-connection loopback marker not found'); s=s.replace(old,rep); fs.writeFileSync(p,s);" \
    && mkdir -p ${DSH_HOME} ${DSH_WORKSPACE}

COPY src/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY src/nginx.conf /etc/nginx/nginx.conf

RUN chmod 0755 /usr/local/bin/entrypoint.sh

EXPOSE 3080

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
