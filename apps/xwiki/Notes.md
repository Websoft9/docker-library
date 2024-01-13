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

By default XWiki ships with an embedded Solr. 但推荐使用外部 solr。官方方案配置外部 solr 还需要挂载一个配置文件，并更改权限，考虑复杂性，暂时不做

3. 安装向导

安装向导会在线拉去资源，故时间比较长

