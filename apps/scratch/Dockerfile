# update time: 202401061124
# This dockerfile build error now, the latest version is v3.0
# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder

LABEL org.opencontainers.image.authors="https://www.websoft9.com" \
      org.opencontainers.image.description="Scratch packaged by Websoft9" \
      org.opencontainers.image.source="https://github.com/Websoft9/docker-library/tree/main/apps/scratch" \
      org.opencontainers.image.title="Scratch" \
      org.opencontainers.image.vendor="Websoft9 Inc." \
      org.opencontainers.image.version="v3.2.37"

RUN apk add --no-cache nano git

RUN git clone --depth=1 https://github.com/scratchfoundation/scratch-gui /data/scratch-gui
RUN cd /data/scratch-gui && npm install && npm run build

FROM nginx:1.15-alpine
COPY --from=builder /data/scratch-gui/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html