#!/bin/bash

echo "get password ..." >> /tmp/init_debug.txt
while [  ! -f /data/apps/jenkins/data/jenkins/secrets/initialAdminPassword ]
do
    sleep 3s
    echo "initing,please wait ..." >> /tmp/init_debug.txt
done
jenkins_pwd=$(sudo cat /data/apps/jenkins/data/jenkins/secrets/initialAdminPassword)
echo "APP_PASSWORD=$jenkins_pwd" >> /data/apps/jenkins/.env
