#!/bin/sh

# 初始化（仅第一次启动时执行）
if [ -f already_init.lock ]; then
  echo "already inital..."
else
  # 修改varnish配置文件
  docker cp wordpresspro_87vfp:/etc/varnish/default.vcl .
  sed -i "s#.host = \".*\";#.host = \"$W9_ID-wordpress\";#g" default.vcl
  docker exec -i wordpresspro_87vfp sh -c 'cat > /etc/varnish/default.vcl' < default.vcl
  docker restart $W9_ID
  # 安装cli
  docker exec $W9_ID-wordpress curl -o wp-cli.phar 'http://proxy.websoft9.com/?url=https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar'
  docker exec $W9_ID-wordpress chmod +x wp-cli.phar
  docker exec $W9_ID-wordpress mv wp-cli.phar /usr/local/bin/wp
  # 完成初始化
  touch already_init.lock
fi

# 等待wordpress完成引导
until docker exec $W9_ID-wordpress wp core is-installed; do
  echo "wait for WordPress..."
  sleep 5
done

# 设置home
if [ "`docker exec $W9_ID-wordpress wp option get home | cut -d: -f1`" == "https" ];then
  docker exec $W9_ID-wordpress wp option update home "https://$W9_URL"
else
  docker exec $W9_ID-wordpress wp option update home "$WORDPRESS_ROOT_URL"
fi

# 设置siteurl
if [ "`docker exec $W9_ID-wordpress wp option get siteurl | cut -d: -f1`" == "https" ];then
  docker exec $W9_ID-wordpress wp option update siteurl "https://$W9_URL"
else
  docker exec $W9_ID-wordpress wp option update siteurl "$WORDPRESS_ROOT_URL"
fi