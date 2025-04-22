## This script is always excused after PHP container running
## If you upload your PHP application source code to container, you should consider migration exist data

if [ -f "/var/www/html/vendor/magento/language-zh_hans_cn/zh_CN.csv" ]; then
  echo "magento site already created, skip it"
  chown -R www-data:www-data /var/www/html
else

  echo "Start to create magento site..."
  sleep 30
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
