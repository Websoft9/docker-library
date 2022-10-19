# Ghost on Docker

![](https://libs.websoft9.com/common/websott9-cloud-installer.png) 

## Introduction

[English](/README.md) | [简体中文](/README-zh.md)  

This repository is an **Cloud Native solution** powered by [Websoft9](https://www.websoft9.com), it simplifies the complicated installation and initialization process.  

## System Requirements

The following are the minimal [recommended requirements](https://hub.docker.com/_/ghost):

* **OS**: Red Hat, CentOS, Debian, Ubuntu or other's Linux OS
* **Public Cloud**: More than 20+ major Cloud such as AWS, Azure, Google Cloud, Alibaba Cloud, HUAWEIClOUD, Tencent Cloud
* **Private Cloud**: KVM, VMware, VirtualBox, OpenStack
* **ARCH**:  Linux x86-64, ARM 32/64, Windows x86-64, IBM POWER8, x86/i686
* **RAM**: 1 GB or more
* **CPU**: 1 cores or higher
* **HDD**: at least 20 GB of free space
* **Swap file**: at least 2 GB
* **bandwidth**: more fluent experience over 100M  

## QuickStart

### All-in-one Installer

Use SSH to connect your instance and run the automatic installation script below

```
sudo wget -N https://raw.githubusercontent.com/Websoft9/StackHub/main/docker-installer.sh; sudo bash docker-installer.sh -r ghost
```
### package install

1.Make package
You can get the  package as following script
```
sudo wget -N https://raw.githubusercontent.com/Websoft9/StackHub/main/docker-installer.sh; sudo bash docker-installer.sh -r ghost -p
```

2.Install by package
Copy package to your server, Use SSH to connect your instance and run the automatic installation script below
```
sudo bash install-ghost
```

### Manual Installation

#### Preparation

If you have not install Docker and Docker-Compose, refer to the following commands to install it:

```
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker
alias docker-compose='docker compose'
echo "alias docker-compose='docker compose'" >> /etc/profile.d/docker-compose.sh
source /etc/profile.d/docker-compose.sh
```

#### Install Ghost

We assume that you are already familiar with Docker, and you can modify [docker-compose file](docker-compose.yml) by yourself

```
git clone --depth=1 https://github.com/Websoft9/docker-ghost
cd docker-ghost
docker network create websoft9 
docker compose  up -d
```

### FAQ

#### Do I need to change the password before docker-compose up?
Yes, you should modify all database password and application password at docker-compose file for production

#### Docker runing failed for the reason that port conflict?
You should modify ports at [docker-compose file](docker-compose-production.yml) and docker-compose again

### Usage instructions

You can point your browser to: *`http://Instance's Internet IP:port`*  

The following is the information that may be needed during use

## Documentation

[Ghost Administrator Guide](https://support.websoft9.com/docs/ghost)

## Enterprise Support

If you want to get our Enterprise Support to ensure high availability of applications, you can subscribe our [Ghost Enterprise Support](https://apps.websoft9.com/ghost) 

What you get with a Enterprise Support subscription?

* Knowledge: Answers and guidance from product experts
* Support: Everything you need for technical support, e.g Enable HTTPS, Upgrade guide
* Security: Security services and tools to protect your software
