sudo echo "alfresco version:" $(docker images |grep alfresco-share |awk '{print $2}') |sudo tee -a /data/logs/install_version.txt
