sudo echo "moodle version": $(docker exec -i $1 cat /bitnami/moodle/version.php  | grep "\$release" | awk '{print $3}' | sed 's/^.//') | tee -a /data/logs/install_version.txt
