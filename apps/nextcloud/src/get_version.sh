sudo echo "nextcloud version:" $(docker exec -i $1 cat version.php |grep OC_VersionString |awk -F "'" '{print $2}') |sudo tee -a /data/logs/install_version.txt
