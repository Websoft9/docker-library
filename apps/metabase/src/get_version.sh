sudo echo "metabase version:" $(curl https://api.github.com/repos/metabase/metabase/releases/latest |jq -r .tag_name) |sudo tee -a /data/logs/install_version.txt
