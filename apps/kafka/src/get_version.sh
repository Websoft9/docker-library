sudo echo "kafka version:" $(docker exec -i $1 /opt/bitnami/kafka/bin/kafka-topics.sh --version) | sudo tee -a /data/logs/install_version.txt
