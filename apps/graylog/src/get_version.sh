sudo echo "graylog version:" $(docker images |grep graylog/graylog |awk '{print $2}')  1>> /data/logs/install_version.txt
