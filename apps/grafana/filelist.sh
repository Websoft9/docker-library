#!/bin/bash

file_list=(
  docker-compose-production*.yml
  .env_all
  README.md
  README-zh.md 
  variables.json
  .git
  .github
)

repo=$(cat ./variables.json |jq -r .name)

fork_url=$(curl -s https://api.github.com/repos/Websoft9/docker-$repo | grep '"html_url"' | sed -n '5p' | awk -F "\"" '{print $4}')

rm -rf /tmp/docker-$repo
git clone --depth=1 $fork_url /tmp/docker-$repo
[[ $? -ne 0 ]] && exit
rm -rf /tmp/docker-$repo/{.git,.github}

unalias cp 1>/dev/null 2>&1

for file in ${file_list[@]}
do
  if [ -f $file ];then
     cp -f $file /tmp/docker-$repo || true
  elif [ -d $file ];then
     cp -arf $file /tmp/docker-$repo || true
  fi
done

if [ -d /tmp/docker-$repo/ ];then
   rm -rf *
   cp -arf /tmp/docker-$repo/* .
fi
rm -rf $0
