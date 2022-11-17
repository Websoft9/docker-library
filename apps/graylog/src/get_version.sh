sudo echo "graylog version:" $(docker image inspect graylog/graylog:$(docker images | grep graylog |awk '{print $2}') | jq .[].Config.Labels | grep "org.label-schema.version" | cut -d ":" -f 2 | sed 's/\"//g') |sudo tee -a /data/logs/install_version.txt

