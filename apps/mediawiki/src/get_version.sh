sudo echo "mediawiki version:" $(docker exec -i mediawiki grep -rn "MediaWiki " /bitnami/mediawiki/LocalSettings.php|awk -F"MediaWiki " '{print $2}') |sudo tee -a /data/logs/install_version.txt
