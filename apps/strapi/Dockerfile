FROM node:22-slim AS build

ARG STRAPI_VERSION=5.54.0

ENV NODE_ENV=production \
    BROWSER=false \
    STRAPI_TELEMETRY_DISABLED=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential python3 git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app

COPY package.json ./
RUN npm install --omit=dev

COPY config ./config
COPY public ./public
COPY src ./src

RUN mkdir -p .tmp public/uploads \
    && npm run build

FROM node:22-slim

ENV NODE_ENV=production \
    BROWSER=false \
    STRAPI_TELEMETRY_DISABLED=true

WORKDIR /opt/app

COPY --from=build /opt/app /opt/app

RUN mkdir -p /opt/app/.tmp /opt/app/public/uploads

EXPOSE 1337

CMD ["npm", "run", "start"]
