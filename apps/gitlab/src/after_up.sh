#!/bin/bash
while [ ! -f /var/lib/docker/volumes/gitlab_gitlab_config/_data/initial_root_password ]
do
    sleep 3
done 
gitlab_pwd=$(sudo grep 'Password:' /var/lib/docker/volumes/gitlab_gitlab_config/_data/initial_root_password|cut -d: -f2)
echo "W9_POWER_PASSWORD=$gitlab_pwd" >> /data/apps/gitlab/.env
echo "W9_PASSWORD=$gitlab_pwd" >> /data/apps/gitlab/.env
