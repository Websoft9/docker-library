# onlyoffice

## Running ONLYOFFICE Docs using HTTPS
[Using HTTPS](https://helpcenter.onlyoffice.com/installation/docs-community-install-docker.aspx) 

Prepare:Ports 80 and 443 are mapped to the host
```
version: '3.8'
services:     
  onlyofficedocs:
    container_name: ${W9_ID}
    image: ${W9_REPO}:${W9_VERSION}
    stdin_open: true
    tty: true
    restart: unless-stopped
    env_file:
      - .env
    ports:
     - 80:80
     - 443:443
```

#### step1: copy createCA.sh to container
```
wget -N https://raw.githubusercontent.com/Websoft9/docker-library/main/apps/onlyofficedocs/src/createCA.sh
docker cp createCA.sh onlyofficedocs:/var/www/onlyoffice/Data
```
#### step2: access the container 
```
docker exec -it onlyofficedocs bash
```
#### step3: run this script 
```
bash /var/www/onlyoffice/Data/createCA.sh
```
#### step4: Modify the container configuration file and restart onlyofficedocs 
Modify the container configuration file "/etc/onlyoffice/documentserver/default. json" and change the value of the "rejectUnauthorized" parameter to "false".

```
sed -i 's/"rejectUnauthorized": true/"rejectUnauthorized": false/g' /etc/onlyoffice/documentserver/default.json
supervisorctl restart all
exit
docker restart onlyofficedocs
```
