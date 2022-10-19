#!/bin/bash
# customrized cmd powered by Websoft9

echo $TYPO3_DB_USER
if [[ -f /var/www/html/wizard ]]; then
    echo "Initialization has been completed before this time!"
else
    echo "" >> /var/www/html/wizard
    sed -i s/127.0.0.1/mysql/g  /var/www/html/typo3_src-11.5.12/typo3/sysext/install/Classes/Controller/InstallerController.php
    cat InstallerController.php |grep username|grep TYPO3_CONF_VARS| awk '{print $NF}'
    cat InstallerController.php |grep username|grep TYPO3_CONF_VARS| awk '{print $NF}'
    
    sed -i "s/\['user'\] ?? ''/['user'] ?? '$TYPO3_DB_USER'/" /var/www/html/typo3_src-11.5.14/typo3/sysext/install/Classes/Controller/InstallerController.php
    sed -i "s/\['password'\] ?? ''/['password'] ?? '$TYPO3_DB_PASSWORD'/" /var/www/html/typo3_src-11.5.14/typo3/sysext/install/Classes/Controller/InstallerController.php
    sed -i "s/\['host'\] ?? '127.0.0.1'/['host'] ?? '$TYPO3_DB_HOST'/" /var/www/html/typo3_src-11.5.14/typo3/sysext/install/Classes/Controller/InstallerController.php
fi
docker-php-entrypoint apache2-foreground
