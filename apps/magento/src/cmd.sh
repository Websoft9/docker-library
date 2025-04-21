## This script is always excused after PHP container running
## If you upload your PHP application source code to container, you should consider migration exist data

if [ -z "$(ls -A /var/www/html)" ]; then
  echo "<?php phpinfo(); ?>" > /var/www/html/index.php
  chown -R www-data:www-data /var/www/html
  echo "Commands executed: index.php created and ownership changed."
else
  echo "Start to create magento site..."
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
fi
