# Oracle Database

This repo is based from [Oracle docker](https://container-registry.oracle.com)

## Edition

Express and Enterprise have different environments, 

## FAQ

#### Express 版本是否可以设置 SID？

官方文档中没有这个环境变量，但设置下面的值没有问题

```
W9_DB_ORACLE_SID=xe
W9_DB_ORACLE_PDB=xepdb1
```

而设置成下面的值会导致数据库无法启动
```
ORACLE_SID=ORCLCDB
ORACLE_PDB=ORCLPDB1
```
