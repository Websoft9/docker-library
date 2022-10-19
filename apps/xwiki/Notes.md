## XWiki

### 安装

1. MySQL 初始化问题

官方文档要求初始化时运行 `grant all privileges on *.* to xwiki@'%'`。但即使不运行这段脚本，查询 xwiki 权限发现也具有 ALL PRIVILEGES 

```
mysql> show grants for xwiki@'%';
+--------------------------------------------------+
| Grants for xwiki@%                               |
+--------------------------------------------------+
| GRANT USAGE ON *.* TO 'xwiki'@'%'                |
| GRANT ALL PRIVILEGES ON `xwiki`.* TO 'xwiki'@'%' |
+--------------------------------------------------+
2 rows in set (0.00 sec)
```

所以暂时不做权限处理。  

2. Solr service

By default XWiki ships with an embedded Solr. 但推荐使用外部 solr

本部署方案已经使用 solr 容器，但暂没验证是否连接成功。  

日志中有一段：  

```
Caused by: org.apache.http.conn.HttpHostConnectException: Connect to localhost:8983 [localhost/127.0.0.1] failed: Connection refused (Connection refused)
```

