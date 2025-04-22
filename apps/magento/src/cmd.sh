## This script is always excused after PHP container running
## If you upload your PHP application source code to container, you should consider migration exist data

# Check MySQL connection
check_mysql() {
  echo "Verifying MySQL connection..."
  mysql -h "${W9_ID}-mariadb" -u magento -p"${W9_RCODE}" -e 'SELECT 1' magento &>/dev/null
  return $?
}

# Check OpenSearch health
check_opensearch() {
  echo "Verifying OpenSearch health..."
  curl -sSf http://${W9_ID}-opensearch:9200/_cluster/health?pretty | grep -q '"status" : "green"'
  return $?
}
  
if [ -f "/var/www/html/vendor/magento/language-zh_hans_cn/zh_CN.csv" ]; then
  echo "magento site already created, skip it"
  chown -R www-data:www-data /var/www/html
else

  echo "Start to create magento site..."

  # DB and OpenSearch must ready before create site
  until check_mysql; do
    sleep 5
  done
  
  until check_opensearch; do
    sleep 5
  done

  # magento create site
  bin/magento setup:install \
  --base-url=http://${W9_URL} \
  --db-host=${W9_ID}-mariadb \
  --db-name=magento \
  --db-user=magento \
  --db-password=${W9_RCODE} \
  --backend-frontname=admin  \
  --admin-firstname=admin \
  --admin-lastname=admin \
  --admin-email=admin@admin.com \
  --admin-user=admin \
  --admin-password=${W9_RCODE} \
  --language=en_US \
  --currency=USD \
  --timezone=America/Chicago \
  --use-rewrites=1 \
  --search-engine=opensearch \
  --opensearch-host=${W9_ID}-opensearch \
  --opensearch-port=9200 \
  --opensearch-index-prefix=magento2 \
  --opensearch-timeout=15 \
  --disable-modules=Magento_TwoFactorAuth 
  
  wget https://websoft9.github.io/docker-library/apps/magento/src/zh_CN.csv -O /var/www/html/vendor/magento/language-zh_hans_cn/zh_CN.csv
  bin/magento setup:static-content:deploy -f zh_Hans_CN
  bin/magento indexer:reindex
  apache2ctl graceful
  chown -R www-data:www-data /var/www/html
fi
