# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder
LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Scratch"

RUN apk add --no-cache nano git

RUN mkdir -p /usr/app/Scratch3
RUN git clone --depth=1 https://github.com/LLK/scratch-gui.git /usr/app/Scratch3
RUN cd usr/app/Scratch3 && npm install && npm run build

FROM nginx:1.15-alpine
COPY --from=builder /usr/app/Scratch3/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html
