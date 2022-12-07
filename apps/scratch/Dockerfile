# fork from : https://github.com/DarkMaguz/scratch3-docker/blob/master/Dockerfile

FROM node:14-alpine as builder
LABEL maintainer="help@websoft9.com"
LABEL version="latest"
LABEL description="Scratch"

RUN apk add --no-cache nano git

RUN git clone --depth=1 https://github.com/LLK/scratch-gui.git /data/scratch-gui ;\
    mkdir -p /data/scratch-gui/build ;\
    cd /data/scratch-gui ;\
    npm install ;\
    npm run build ;\
    sed -i "s/'process.env.GA_ID'.*//g" webpack.config.js ;\
    sed -i "s/process.env.DEBUG.*/process.env.DEBUG\': Boolean(process.env.DEBUG)/g" webpack.config.js ;\
    sed -i 's/`https.*/`.\/static\/assets\/\${iconMd5}` :/g' src/containers/library-item.jsx ;\
    sed -i 's/${this.assetHost}\/internalapi.*/.\/static\/assets\/\${asset.assetId}.\${asset.dataFormat}`;/g' src/lib/storage.js ;\
    cd build/static/assets && ls

FROM nginx:1.15-alpine
COPY --from=builder /data/scratch-gui/build /usr/share/nginx/html
VOLUME /usr/share/nginx/html
