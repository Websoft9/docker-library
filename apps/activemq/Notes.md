# ActiveMQ

* Classic: https://activemq.apache.org/components/classic/download/
* Artemis: https://github.com/apache/activemq-artemis/tree/main/artemis-docker

官方没有提供 Classic 镜像以及Dockerfile；  
官方提供了 Artemis Docker 仓库，且维护及时，但官方没有发布镜像，需自行构建。


## Build Artemis image

### 官方方案

```
./prepare-docker.sh --from-release --artemis-version 2.22.0
cd _TMP_/artemis/2.22.0
#准备二进制bin目录
tar -zxvf apache-artemis-2.22.0-bin.tar.gz; cp -r ./apache*/*  ./
docker build -f ./docker/Dockerfile-debian -t artemis-debian .
```

但构建的容器运行报错，暂无解决方案  

### 第三方镜像

基于官方的 docker 文件构建：https://github.com/ls1intum/activemq-broker-docker/pkgs/container/activemq-broker-docker-centos

## Docker for Classic

积极维护的几个项目：  

* https://github.com/tec-cloud/docker-activemq
* https://github.com/Alfresco/alfresco-docker-activemq
* https://github.com/TremoloSecurity/activemq-docker
* https://github.com/quotidian-ennui/docker-activemq
* https://hub.docker.com/r/rmohr/activemq/dockerfile/#!

其中 alfresco 维护较好，故选用它

## Multiply version

command `docker-compose --profile classic up -d`

or

delete profiles tag at docker-compose.yml which you want to use