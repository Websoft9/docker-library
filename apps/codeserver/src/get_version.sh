sudo echo "codeserver version:" $(docker inspect codeserver | grep org.opencontainers.image.version | cut -d: -f2) 1>> /data/logs/install_version.txt
