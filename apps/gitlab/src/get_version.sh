sudo echo "gitlab version:" $(docker exec -i gitlab head -n+1 /opt/gitlab/version-manifest.txt) |sudo  tee -a /data/logs/install_version.txt
