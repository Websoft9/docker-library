#!/bin/bash
# customized cmd powered by Websoft9

echo "TYPO3 DB User: $TYPO3_DB_USER"
if [[ -f /var/www/html/wizard ]]; then
    echo "Initialization has been completed before this time!"
else
    # 标记初始化已完成
    touch /var/www/html/wizard

    # 定义 InstallerController.php 文件的路径模式
    installer_pattern="/var/www/html/typo3_src-*/typo3/sysext/install/Classes/Controller/InstallerController.php"

    # 使用定义的路径模式查找文件，并对每个文件执行 sed 替换
    find /var/www/html -type f -path "$installer_pattern" -exec sed -i "s/127.0.0.1/mysql/g" {} \;
    find /var/www/html -type f -path "$installer_pattern" -exec sed -i "s/\['user'\] ?? ''/\['user'\] ?? '$TYPO3_DB_USER'/" {} \;
    find /var/www/html -type f -path "$installer_pattern" -exec sed -i "s/\['password'\] ?? ''/\['password'\] ?? '$TYPO3_DB_PASSWORD'/" {} \;
    find /var/www/html -type f -path "$installer_pattern" -exec sed -i "s/\['host'\] ?? '127.0.0.1'/\['host'\] ?? '$TYPO3_DB_HOST'/" {} \;
fi

# 启动 Apache
docker-php-entrypoint apache2-foreground