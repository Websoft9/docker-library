# Developer Guide

- Write the dockerfile if there no suitale image for the application
- Write the docker-compose file and .env as per specifications
- Test it and pull request

Our specifications is very simple, you just only add the environments begin with **APP\_** reference from template

## Architecture

The architecture of the library is relatively simple, which is a collection of a large number of apps that are uniformly placed in the apps director. Each folder under apps is an independent and runnable Docker Compose project.

## Docker compose

You can understand the basic composition and specifications through the [Docker Compose template file](../template/docker-compose.yml), The following points will help you quickly integrate into library project.

### Use official docker image

Try to use the official image as much as possible, unless there is no maintenance or updates have been stopped.

And you can also get image from public image hub:

- [DockerHub](https://hub.docker.com/)
- [Amazon ECR Public Gallery](https://gallery.ecr.aws)

### Microservices

The images used should be componentized as much as possible, with app main images and DB images, and web server images connected to achieve software availability.

### Networks

All containers are placed on the network named **websoft9**, making them accessible to each other through container names.

### Volumes

We define all the names that need to be mounted at the end of docker-compose.yml and use them through references in different container.

### Health check

Whether the container starts normally through [Health check](https://docs.docker.com/engine/reference/builder/#healthcheck)

### Container name

The main container is named $W9_ID, and other containers add a suffix to $W9_ID, such as $W9_ID-mysql.When container connections cannot be adapted to the common rules above, there are two ways to correspond:

  - Add hostname, named $W9_RCODE
  - Container named servicename-$W9_RCODE
 
### Logs limit

Some application have lots of logs which will need storages. If you want to limit it, below is referance

```
  wordpress:
    image: wordpress:$W9_VERSION
    container_name: $W9_NAME
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
          max-file: "5"
          max-size: 10m
```

### Bind mount

Suggest use the unified bind mount *src* which include config or script files for creating/modify application.

| file name          | Description                                                                                                                                                          | Necessity |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| nginx_proxy.conf         | nginx config code section which will insert to server{} by websoft9 api, and it can override the exist location                                 | no        |
| php_exra.ini         | extra php.ini for PHP application, you can add it to docker-compose.yml if you want to use it                    | no        |


> you should add **proxy_pass  $forward_scheme://$server:$port$request_uri;** to your nginx_proxy.conf if you override default location /{}

## Environments

The environment variables of the container is the interface between the container and external interactions, the library all of the apps's environment variables are imported through **.env** file and cannot be directly defined in the docker-compose.yml, you can understand the basic composition and specifications through the [.env template file](../template/.env).

The environments begin with **APP\_** is core environment variables. Generally speaking, developers only define and use them.
We will list and explain commonly used environmental variables as following table:

| Variable name          | Description                                                                                                                                                          | Necessity |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------- |
| W9_REPO     | The main container docker image url                                                                                                              | no        |
| W9_DIST     | The edition of main application                                       | no        |
| W9_VERSION            | The version of this application, the image's tag of main container                                                                                                   | yes       |
| W9_POWER_PASSWORD         | Original Password, all containers password in the Docker Compose are setted to this password, make all container passwords the same                                  | no        |
| W9_HTTP_PORT_SET     | The main port of this web application, you can access this application by http://ip:W9_HTTP_PORT_SET                                                                      | no        |
| W9_HTTPS_PORT_SET     | The main port of this web application, you can access this application by https://ip:W9_HTTPs_PORT_SET                                                                      | no        |
| W9_DB_PORT_SET          | The database's port when application is a Database | no        |
| W9_MQ_PORT_SET          | The MQ's port when application is a MQ | no        |
| W9_SSH_PORT_SET         | The extra ssh port of a aplication, such as gitlab | no        |
| W9_ID               | The name of this application, main container also named by **W9_NAME's** value                                                                                      | yes       |\
| W9_NAME               | The application name,such as wordpress,mysql                                             | yes       |
| W9_URL_REPLACE        | You must modify W9_URL on init when it is true                                                                                                                      | no        |
| W9_URL                | It is used when the application APP needs to set an external URL, which can be IP(or domain), IP:PORT, http(s)://IP:POR                                              | no        |
| W9_ADMIN_PATH         | Application's background access address is main url and this suffix                                                                                                  | no        |
| W9_LOGIN_USER               | Application's login username                                                                                                                                         | no        |
| W9_LOGIN_PASSWORD           | Application's login password                                                                                                                                         | no        |
| W9_ENCRYPT_PASSWORD   | Some application must use password with encryption                                                                                                                   | no        |
| W9_DB_EXPOSE  | Main database of application                                                                                            | no        |
| W9_HTTP_PORT     | Main container internal http port                                                                                                                              | no        |
| W9_HTTPS_PORT     | Main container internal https port                                                                                                        | no        |
| W9_NETWORK            | We have uniformly created a network named constant **websoft9**, which ensures that multiple applications can easily access it through the container name if needed  | yes       |


> main container: When the container has web pages, the corresponding container of the page is the main container; When a container has no pages, the corresponding container for the core application is usually the main container.


## Dockerfile

When we cannot find a suitable image, we have to compile the image by Dockerfile,We make a requirement in the following aspects.

### Parent Image

The parent image needs to follow the following point:

- The preferred image is the one provided by the official, as the official image has undergone extensive testing and verification, and has good stability and reliability.
- Select the smallest possible base image to reduce the size of the image and potential security vulnerabilities.
- Select images that have undergone security review and frequent updates.

### Files path

Main related files are all placed in two directories:

- root directory: Dockerfile, cmd.sh, entrypoint.sh
- src directory: config files or need to edit executable files

### Maintainability

Sufficient external interfaces need to be provided through environment variables, such as username,passowrd,port.

### LABEL

The elements of label are necessary: such as version,vendor,description.

## Configure fils

Configure files use src to mount to container

### PHP

1. Docker official image or Bitnami image have different method for php configuration
2. Docker official image need mount php_exra.ini to container
3. Bitnami image have envs of php configuration
4. As a reference, other php application should check if php conf.d directoy exist in container, mount php_exra.ini to this path

### MySQL 

## Metedata and Docs

### variables.json

Every application must contain a variables.json, which contains information such as version, trademark, document reference address, and running environment requirements.

### Notes

Record some important items to remind all contributors.

### CHANGELOG.md

Change logs

## FAQ

#### How to create new application?

Create new application must use [template](../template/), then set your file:  

1. docker-compose.yml

- Docker image address using environment variables
- Do not expose external ports in the main database and message queue of web applications
- Each container must directly reference. env
- Use after declaring volumes
- The configuration file volumes uses the absolute path reference of src

2. .env

- Custom environment variables start with W9
- Place the environment variables of the container itself last of .env
- All exposed ports are marked with End of _SET, users can modify them
- These variables must be included in .env: W9_REPO, W9_DIST, W9_VERSION, W9_ID
- W9_URL is an identifier that distinguishes web applications
- There are two internal ports in the web application container: W9_HTTP_PORT, W9_HTTPS_PORT
- The user's main database type is W9_ DB_ EXPOSE to determine

#### Which environments added to .env file?

You know there three type container for an application:

- Application container
- Application assisting container: Which help application container for automatic install wizard, monitor...
- Independent Service: e.g database, mq, redis

We suggest add Application container and Application assisting container 's environments to .env

#### Which version should use?

Try to use x.x, not recommend use x.x.x if not necessary.