[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)
[![GitHub Release Date](https://img.shields.io/github/release-date/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)
[![GitHub Repo stars](https://img.shields.io/github/stars/Websoft9/docker-library?style=social)](https://github.com/Websoft9/docker-library)

# Docker Compose applications

This repository include [200+ applications](https://github.com/Websoft9/docker-library/tree/main/apps) based on [Docker compose](https://docs.docker.com/compose/), e.g WordPress, MySQL, Odoo, MongoDB, GitLab, Elastic, Ghost, Grafana, Graylog, Kafka, n8n, Moodle, Nextcloud, ONLYOFFICE, phpMyAdmin...

You can use them for bussiness management, content management, data analysis, development, DevOps and any things you want to do.  


## How to use it?

The easiest way is install [ Websoft9](https://github.com/Websoft9/websoft9) which can help you running these applications on web-based console.  

Of course, you can also use Docker compose to running these application: 

1. Make sure you have install the Docker latest or you can install Docker by below script

   ```
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo systemctl enable docker && sudo systemctl start docker
   ```

2. Download this repository to your Linux and list all applications

   ```
   git clone --depth=1 https://github.com/Websoft9/docker-library
   cd docker-library && ls apps
   ```

3. Go to the target app directory, check or modify the [.env](https://github.com/Websoft9/docker-library/blob/main/docs/code_owner.md#environment-variables), then run it

   ```
   # e.g install wordpress
   cd apps/wordpress
   sudo docker network create websoft9 &&  sudo docker compose up -d
   ```

## How to contribute it?

We greatly welcome community contributions to provide suggestions and improvements to our project:

1. Find a bug, request features and provide better methods, you can promote your ideas through [issue](https://github.com/Websoft9/docker-library/issues).

2. Contributing to this repository, please follow our [contribution guidelines](CONTRIBUTING.md). We try our best to provide [reward](./docs/reward.md) for some important task.

## Documentation

[Websoft9 Administrator Guide](https://support.websoft9.com/docs/apps)

## Support

You can subscribe [Websoft9 Enterprise Support](https://www.websoft9.com/apps) to ensure high availability of applications and more:

- Knowledge: Answers and guidance from product experts
- Support: Everything you need for technical support, e.g Enable HTTPS, Upgrade guide
- Security: Security services and tools to protect your software

## Sponsor

The following corporate organizations have provided us with sponsorship, which has greatly helped this repository.

![image](https://libs.websoft9.com/Websoft9/logo/sponser/50sponser-huawei-logo.png) ![image](https://libs.websoft9.com/Websoft9/logo/sponser/50sponser-mingdaoyun-logo.png) ![image](https://libs.websoft9.com/Websoft9/logo/sponser/50sponser-apitable-logo.png)

## License

[LGPL-3.0](LICENSE.md), Additional Terms: It is not allowed to publish free or paid image based on this repository in any Cloud platform's Marketplace without authorization.

## Disclaimer

We can't guarantee the open source software does not have vulnerability or the security risks which is the responsibility of user according to the open source licenses.

## App Wishlist

Propose and vote for [apps](wishlist.md) to be packaged

## FAQ

#### Do I need to change the password before docker-compose up?

Yes, you should modify **POWER_PASSWORD** at .env file for production

#### Docker runing failed for the reason that port conflict?

You should modify **APP\_\*\_PORT** at .env file

#### What the credentials for application?

W9_USER, W9_PASSWORD

#### Is there any infrastructure limit?

No, you can use lots of infrastructure, e.g.

- **OS**: Red Hat, CentOS, Debian, Ubuntu or other's Linux OS ...
- **Public Cloud**: More than 20+ major Cloud such as AWS, Azure, Google Cloud, Alibaba Cloud, HUAWEIClOUD, Oracle Cloud ...
- **Private Cloud**: KVM, VMware, VirtualBox, OpenStack ...
- **ARCH**: Linux x86-64, ARM 32/64, x86/i686 ...
