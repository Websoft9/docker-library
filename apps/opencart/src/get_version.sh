sudo echo "opencart version:" $(cat /data/apps/opencart/data/opencart/index.php |grep VERSION |cut -d"'" -f4) |sudo tee -a /data/logs/install_version.txt
