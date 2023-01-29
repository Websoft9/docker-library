sudo echo "dolibarr version:" $(docker image  inspect tuxgasy/dolibarr | grep DOLI_VERSION  | cut -d "=" -f 2 | sed 's/",//')  1>> /data/logs/install_version.txt
