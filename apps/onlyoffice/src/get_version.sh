sudo echo $(docker inspect onlyoffice/communityserver |grep onlyoffice.community.version |sed -n 1p |sed 's/"/ /g') |awk '{print $1 $2,$3}' | tee -a /data/logs/install_version.txt
