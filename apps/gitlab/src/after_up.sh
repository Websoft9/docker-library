#!/bin/bash
while [ ! -f /var/lib/docker/volumes/gitlab_gitlab_config/_data/initial_root_password ]
do
    sleep 3
    echo "1111" >> /tmp/gitlab
done 
gitlab_pwd=$(sudo grep 'Password:' /var/lib/docker/volumes/gitlab_gitlab_config/_data/initial_root_password|cut -d: -f2)
echo "POWER_PASSWORD=$gitlab_pwd" >> /data/apps/gitlab/.env
echo "APP_PASSWORD=$gitlab_pwd" >> /data/apps/gitlab/.env
