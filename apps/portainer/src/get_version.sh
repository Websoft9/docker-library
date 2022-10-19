sudo echo Portainer Version:$(curl https://github.com/portainer/portainer/releases |grep Release |grep tag |head -1 |cut -d/ -f6 |cut -c 1-6) 1>> /data/logs/install_version.txt
