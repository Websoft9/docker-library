#!/bin/sh
files=$(ls apps/)
for file in $files
do
  if [ -f apps/$file/docker-compose.yml ];then
    sed -i 's/restart: unless-stopped/restart: always/g' apps/$file/docker-compose.yml
  else 
    echo "apps/$file/docker-compose.yml dosen't exist"
  fi
done
