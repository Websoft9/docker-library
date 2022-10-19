sudo echo "drupal version:" $(docker exec -it $1 cat /opt/bitnami/drupal/core/lib/Drupal.php |grep -i "const version" |awk -F "'" '{print  $2}') |sudo tee -a /data/logs/install_version.txt
