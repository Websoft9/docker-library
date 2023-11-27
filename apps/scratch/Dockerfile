# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder
LABEL maintainer="help@websoft9.com"
LABEL version="v3.2.37"
LABEL description="Scratch"

RUN apk add --no-cache nano git

RUN git clone --depth=1 https://github.com/scratchfoundation/scratch-gui /data/scratch-gui
RUN cd /data/scratch-gui && npm install && npm run build

FROM nginx:1.15-alpine
COPY --from=builder /data/scratch-gui/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html