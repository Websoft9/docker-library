## This script is always excused after PHP container running
## If you upload your PHP application source code to container, you should consider migration exist data

# Check MySQL connection
check_mysql() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Verifying MySQL connection..."
  mysql -h "${MAGENTO_DB_HOST}" -u magento -p"${MAGENTO_DB_PASSWORD}" -e 'SELECT 1' magento &>/dev/null
  return $?
}

# Check OpenSearch health
check_opensearch() {
  echo "[$(date +'%Y-%m-%d %H:%M:%S')] Verifying OpenSearch health..."
  curl -sSf http://${MAGENTO_OPENSEARCH_HOST}:9200/_cluster/health?pretty | grep -q '"status" : "green"'
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
  --base-url=http://${MAGENTO_URL} \
  --db-host=${MAGENTO_DB_HOST} \
  --db-name=${MAGENTO_DB_NAME} \
  --db-user=${MAGENTO_DB_USER} \
  --db-password=${MAGENTO_DB_PASSWORD} \
  --backend-frontname=${MAGENTO_ADMIN_PATH}  \
  --admin-firstname=James \
  --admin-lastname=Smith \
  --admin-email=admin@admin.com \
  --admin-user=${MAGENTO_ADMIN_USER} \
  --admin-password=${MAGENTO_ADMIN_PASSWORD} \
  --language=en_US \
  --currency=USD \
  --timezone=America/Chicago \
  --use-rewrites=1 \
  --search-engine=opensearch \
  --opensearch-host=${MAGENTO_OPENSEARCH_HOST} \
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
