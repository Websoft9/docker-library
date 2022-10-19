sudo echo Odoo Version:$(docker exec -it $1 odoo --version) 1>> /data/logs/install_version.txt
