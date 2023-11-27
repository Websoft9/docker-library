# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder
LABEL maintainer="help@websoft9.com"
LABEL version="3.2.37"
LABEL description="Scratch"

ENV SCRATCH_VERSION=v3.2.37
ENV scratch_repo="https://github.com/scratchfoundation/scratch-gui/archive/refs/tags"
ENV file_type=".zip"
RUN apk add --no-cache nano git
RUN wget $scratch_repo/$SCRATCH_VERSION$file_type && unzip $SCRATCH_VERSION$file_type && mkdir /data/ && mv scratch-gui* /data/scratch-gui
RUN cd /data/scratch-gui && npm install
RUN cd /data/scratch-gui && npm run build

FROM nginx:1.15-alpine
COPY --from=builder /data/scratch-gui/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html
