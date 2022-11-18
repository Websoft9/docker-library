# Websoft9 Docker applications

If you can use docker, you already know how to use and develop an app for Websoft9. 

## How to use it?

Just need docker compose, you can use them very easy

1. Make sure you have install the Docker latest or you can install Docker by below script

   ```
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && sudo systemctl start docker
   ```

2. Download this repository to your Linux system and list all applications

   ```
   git clone https://github.com/Websoft9/docker-library
   cd docker-library && ls apps
   ```

3. Go to the target app directory, then run it

   ```
   # e.g install wordpress
   cd apps/wordpress
   sudo docker compose up -d
   ```

## Environments

All environment is at `.env` file for each application, You should read it and modify it if you need.

These environments is frequently used:  

* POWER_PASSWORD: It can be used for Database password or Administrator password, you should reset it
* APP_URL: You must reset it for you real DND or IP if APP_URL_REPLACE=true
* APP_HTTP_PORT
* APP_ENCRYPT_PASSWORD: This value is from encrypt APP_PASSWOR, some image use encrypted environment
* APP_AUTH_NEED

## Develop for it

The development for this repository have below field: 

* Write the dockerfile if there no suitale image for the application
* Write the docker-compose file and .env as per specifications
* Test it and pull request

Our specifications is very simple, you just only add the environments begin with **APP_** reference from template

## Paid Issue

We will certainly encounter difficult problems in our work, but it may be very simple for you. So, Websoft9 will pay for some important issue, you can see these issue with "¥50 - ¥1000" . Hope you can close it and obtain the reward
