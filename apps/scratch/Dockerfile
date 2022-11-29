# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder
LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Scratch"

RUN apk add --no-cache nano git

RUN mkdir -p/data/scratch-gui ;\
    mkdir -p /data/scratch-desktop ;\
    git clone --depth=1 https://github.com/LLK/scratch-gui /data/scratch-gui ;\
    git clone --depth=1 https://github.com/LLK/scratch-desktop /data/scratch-desktop ;\
    npm install ;\
    npm run fetch ;\
    cp -r /data/scratch-desktop/static/assets/* /data/scratch-gui/static/assets/* ;\
    sed -i "s/'process.env.GA_ID'.*//g" /data/scratch-gui/webpack.config.js ;\
    sed -i 's/`https.*/`.\/static\/asset\/\${iconMd5}` :/g' /data/scratch-gui/src/containers/library-item.jsx ;\
    sed -i 's/${this.assetHost}\/internalapi.*/.\/static\/asset\/\${asset.assetId}.\${asset.dataFormat}`;/g' /data/scratch-gui/src/lib/storage.js

FROM nginx:1.15-alpine
COPY --from=builder /data/scratch-gui/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html
