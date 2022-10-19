sudo echo "magento version:" $(docker exec -i magento cat /bitnami/magento/composer.json|grep \"version\":|cut -d: -f2) |sudo tee -a /data/logs/install_version.txt
