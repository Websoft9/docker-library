[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](http://www.gnu.org/licenses/gpl-3.0)
[![GitHub last commit](https://img.shields.io/github/last-commit/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)
[![GitHub Release Date](https://img.shields.io/github/release-date/Websoft9/docker-library)](https://github.com/Websoft9/docker-library)
[![GitHub Repo stars](https://img.shields.io/github/stars/Websoft9/docker-library?style=social)](https://github.com/Websoft9/docker-library)

# Docker Compose applications

This repository include 200+ applications based on docker compose, e.g [WordPress, MySQL, Odoo, MongoDB, GitLab, Elastic, Ghost, Grafana, Graylog, Kafka, n8n, Moodle, Nextcloud, ONLYOFFICE, phpMyAdmin...](https://github.com/Websoft9/docker-library/tree/main/apps).

You can use them for bussiness management, content management, data analysis, development, DevOps and any things you want to do.

We will try our best to use official images and will not intentionally maintain Docker images for each app on Docker Hub, focusing on the arrangement and connection between containers. If you can use docker, you already know how to use and develop an application for [Websoft9](https://www.websoft9.com).

## How to use it?

All these applications integrated to [Websoft9](https://github.com/Websoft9/websoft9) which is a web-based PaaS platform on single machine.
The appstore menu will display all of applications in the library, you can click **Install** to use the application you want.

If you don't want to use the **Websoft9**, you can also quickly install it through scripts.

### Quickstart

1. Make sure you have install the Docker latest or you can install Docker by below script

   ```
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo systemctl enable docker && sudo systemctl start docker
   ```

2. Download this repository to your Linux and list all applications

   ```
   git clone https://github.com/Websoft9/docker-library
   cd docker-library && ls apps
   ```

3. Go to the target app directory, check the .env, then run it

   ```
   # e.g install wordpress
   cd apps/wordpress
   sudo docker network create websoft9 &&  sudo docker compose up -d
   ```

### Environments

All environments is in the `.env` file, you should read [Env Guide](https://github.com/Websoft9/docker-library/blob/main/docs/code_owner.md#environment-variables) when you run a app by docker compose.

## How to contribute it?

We greatly welcome community contributions to provide suggestions and improvements to our project:

1. Participate this repository through [issue](https://github.com/Websoft9/docker-library/issues)

   If you find a bug, request new features or provide better methods to solve the problem, you can promote your ideas through issues.

2. Contributing to the docker-library repository, some times will have reward for it.
   Please follow our [contribution guidelines](CONTRIBUTING.md) when making a contribution.

> [this repository reward detail](./docs/paid.md)

## Documentation

[Websoft9 Administrator Guide](https://support.websoft9.com/docs)

## Support

You can subscribe [Websoft9 Enterprise Support](https://www.websoft9.com/apps) to ensure high availability of applications and more:

- Knowledge: Answers and guidance from product experts
- Support: Everything you need for technical support, e.g Enable HTTPS, Upgrade guide
- Security: Security services and tools to protect your software

## Sponsor

The following corporate organizations have provided us with sponsorship, which has greatly helped the repository: [APITable](https://apitable.com/), [Mingdao](https://www.mingdao.com/), [HUAWEI CLOUD](https://www.huaweicloud.com/intl/en-us/).

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

APP_USER, APP_PASSWORD

#### Is there any infrastructure limit?

No, you can use lots of infrastructure, e.g.

- **OS**: Red Hat, CentOS, Debian, Ubuntu or other's Linux OS ...
- **Public Cloud**: More than 20+ major Cloud such as AWS, Azure, Google Cloud, Alibaba Cloud, HUAWEIClOUD, Tencent Cloud, Oracle Cloud ...
- **Private Cloud**: KVM, VMware, VirtualBox, OpenStack ...
- **ARCH**: Linux x86-64, ARM 32/64, x86/i686 ...
