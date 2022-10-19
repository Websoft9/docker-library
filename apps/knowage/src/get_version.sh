sudo echo "knowage version:" $(docker images |grep knowagelabs |awk '{print $2}' |head -1 |cut -d- -f1) |sudo tee -a /data/logs/install_version.txt 
