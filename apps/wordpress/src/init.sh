#!/bin/sh

# 初始化（仅第一次启动时执行）
if [ -f already_init.lock ]; then
  echo "already inital..."
else
  # 安装cli
  docker exec $W9_ID curl -o wp-cli.phar 'http://proxy.websoft9.com/?url=https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar'
  docker exec $W9_ID chmod +x wp-cli.phar
  docker exec $W9_ID mv wp-cli.phar /usr/local/bin/wp
  # 完成初始化
  touch already_init.lock
fi

# 等待wordpress完成引导
until docker exec $W9_ID wp core is-installed >/dev/null 2>&1; do
  echo "wait for WordPress..."
  sleep 5
done

# W9_URL为空时跳过URL更新，避免将站点URL设为无效值
if [ -z "$W9_URL" ]; then
  echo "W9_URL is empty, skip URL update"
  exit 0
fi

# 设置home和siteurl
docker exec $W9_ID wp option update home "$WORDPRESS_ROOT_URL"
docker exec $W9_ID wp option update siteurl "$WORDPRESS_ROOT_URL"