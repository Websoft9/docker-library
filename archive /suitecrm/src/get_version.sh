sudo echo "suitecrm version:" $(docker exec -i $1 cat /bitnami/suitecrm/VERSION) |sudo tee -a /data/logs/install_version.txt
