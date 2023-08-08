# Developer Guide

- Write the dockerfile if there no suitale image for the application
- Write the docker-compose file and .env as per specifications
- Test it and pull request

Our specifications is very simple, you just only add the environments begin with **APP\_** reference from template

## Architecture

The architecture of the library is relatively simple, which is a collection of a large number of apps that are uniformly placed in the apps director. Each folder under apps is an independent and runnable Docker Compose project.

## Docker-compose

You can learn a lot of key information through the [Docker Compose template file](../template/docker-compose.yml), The following points will help you quickly integrate into library project.

### Use official docker image

Try to use the official image as much as possible, unless there is no maintenance or updates have been stopped.   

And you can also get image from public image hub:  

* [DockerHub](https://hub.docker.com/)
* [Amazon ECR Public Gallery](https://gallery.ecr.aws)

### Microservices

The images used should be componentized as much as possible, with app main images and DB images, and web server images connected to achieve software availability.

### Networks

All containers are placed on the same network, making them accessible to each other through container names.

### Volumes

Do not use absolute paths, reference by defining volumes.

## Env_file

表格罗列说明
You can learn a lot of key information through the [.env template file](../template/.env), we forcibly name it .env, do not use other names.

### Generic variable

Variables included in all app:

- APP_NAME: It is required in .env file, main container is setted with APP_NAME.

> When the container has web pages, the corresponding container of the page is the main container; When a container has no pages, the corresponding container for the core application is usually the main container

- APP_VERSION: It is required in .env file, the app's version.

- APP_NETWORK: It is required in .env file, We uniformly place all apps under the network named APP_NETWORK to facilitate connections before the container

### Important variable

- POWER_PASSWORD: If app or db have password, init password is POWER_PASSWORD. APP_PASSWORD and DB_PASSWORD uses it to assign values and maintain the same password for one app

- APP_HTTP_PORT: When the container has web pages, use it to map to an external network port for internet access.

- APP_URL: It is used when the application APP needs to set an external URL, which can be IP(or domain), IP:PORT, http(s)://IP:PORT

- APP_URL_REPLACE: modifies APP_URL on init when it is true

- APP_ADMIN_PATH: App's background access address

- APP_HTTPS_ACCESS: some container (e.g teleport) need HTTPS access, then need to set this pra

#### DB related variable

The database type needs to be included in the middle of the variable, such as mysql,mongodb,postgresql,(e.g mysql):

```
APP_DB_MYSQL_VERSION=5.7
APP_DB_MYSQL_PORT=3306
APP_DB_MYSQL_PASSWORD=$APP_PASSWORD
APP_DB_MYSQL_NAME=$APP_NAME
APP_DB_MYSQL_USER=$APP_NAME
```

## Dockerfile

### Files structure

Compilation related files are all placed in two directories:

- App's root directory: Dockerfile, cmd.sh, entrypoint.sh

- App's src directory: config files or need to edit executable files

### Maintainability

Version, username, and password should be set as environment variables as much as possible to facilitate user changes or subsequent upgrades.

## Credentials

## Health check

## Logs limit

Some application have lots of logs which will need storages. If you want to limit it, below is referance

```
  wordpress:
    image: wordpress:$APP_VERSION
    container_name: $APP_NAME
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
          max-file: "5"
          max-size: 10m
```

## PHP configuration

1. Docker official image or Bitnami image have different method for php configuration
2. Docker official image need mount php_exra.ini to container
3. Bitnami image have envs of php configuration

## variables.json

- version format: x.x.x
