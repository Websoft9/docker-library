
sudo echo OnlyofficeDocs Version:$(docker exec -i $1 bash -c 'apt-cache show onlyoffice-documentserver |grep -i version |cut -d: -f2') 1>> /data/logs/install_version.txt
