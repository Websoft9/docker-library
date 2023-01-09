sudo echo "moodle version": $(docker exec -i moodle cat /bitnami/moodle/licenses/gpl-source-links.txt | cut -d "," -f 1 | cut -d "-" -f 2) | tee -a /data/logs/install_version.txt
