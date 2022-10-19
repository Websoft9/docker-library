#!/bin/bash
sleep 60s
gitlab_pwd=$(sudo grep 'Password:' /data/apps/gitlab/data/gitlab_config/initial_root_password|cut -d: -f2)

echo "APP_PASSWORD=$gitlab_pwd" >> /data/apps/gitlab/.env
