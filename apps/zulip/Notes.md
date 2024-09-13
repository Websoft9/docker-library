# install zulip
## When installing, it is necessary to bind the domain name, otherwise the installation will fail
## After installation, it is necessary to apply for SSL certificate from nginx

##  Create a Zulip organization
```
docker exec -it container_name bash
su zulip -c /home/zulip/deployments/current/manage.py generate_realm_creation_link
```
