# onlyoffice

## Running ONLYOFFICE Docs using HTTPS
[Using HTTPS](https://helpcenter.onlyoffice.com/installation/docs-community-install-docker.aspx) 

#### step1: copy createCA.sh to container
```
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
#### step4: exit the container and restart onlyofficedocs 
```
exit
docker restart onlyofficedocs
```
