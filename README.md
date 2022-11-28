# Websoft9 Docker applications

This repository include 200+ applications based on docker compose, e.g [WordPress, MySQL, Odoo, MongoDB...](https://github.com/Websoft9/docker-library/tree/main/apps) 

If you can use docker, you already know how to use and develop an application for [Websoft9](https://www.websoft9.com). 

## How to use it?


1. Make sure you have install the Docker latest or you can install Docker by below script

   ```
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo systemctl start docker
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

## Environments

All environment is at `.env` file for each application, You should read it and modify it if you need.

These environments is frequently used:  

* POWER_PASSWORD: It can be used for Database password or Administrator password, you should reset it
* APP_URL: You must reset it for you real DNS or IP if APP_URL_REPLACE=true
* APP_HTTP_PORT
* APP_ENCRYPT_PASSWORD: This value is from encrypt APP_PASSWOR, some image use encrypted environment
* APP_AUTH_NEED

## Develop for it

The development for this repository have below field: 

* Write the dockerfile if there no suitale image for the application
* Write the docker-compose file and .env as per specifications
* Test it and pull request

Our specifications is very simple, you just only add the environments begin with **APP_** reference from template

## Issue reward

We will certainly encounter difficult problems in our work, but it may be very simple for you.   

Websoft9 submit some issue with "¥50 - ¥1000", hope you can close it and obtain the reward

## Documentation

[Websoft9 Administrator Guide](https://support.websoft9.com/docs)

## Support

You can subscribe [Websoft9 Enterprise Support](https://www.websoft9.com/apps) to ensure high availability of applications and more:  

* Knowledge: Answers and guidance from product experts
* Support: Everything you need for technical support, e.g Enable HTTPS, Upgrade guide
* Security: Security services and tools to protect your software

## License

[LGPL-3.0](/License.md), Additional Terms: It is not allowed to publish free or paid image based on this repository in any Cloud platform's Marketplace without authorization (未经授权许可，不允许将基于本项目创建的镜像到云平台市场上售卖)
