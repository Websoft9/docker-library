## This script is always excused after PHP container running
## If you upload your PHP application source code to container, you should consider migration exist data

## Sample for you

if [ -z "$(ls -A /var/www/html)" ]; then
  echo "<?php phpinfo(); ?>" > /var/www/html/index.php
  chown -R www-data:www-data /var/www/html
  echo "Commands executed: index.php created and ownership changed."
else
  echo "/var/www/html is not empty. No actions taken."
fi