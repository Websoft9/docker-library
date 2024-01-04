# Oracle Database

This repo is based from [Oracle docker](https://container-registry.oracle.com)

## Edition

- Express and Enterprise have different environments
- Free edition vs Express edition

## FAQ

#### Express 版本是否可以设置 SID？

官方文档中没有这个环境变量，但设置下面的值没有问题

```
ORACLE_EX_SID=xe
ORACLE_EX_PDB=xepdb1
```

而设置成下面的值会导致数据库无法启动
```
ORACLE_EX_SID=ORCLCDB
ORACLE_EX_PDB=ORCLPDB1
```

#### 怎么访问 EM？

https://IP:5500/em

#### CloudBeaver 连接

![image](https://github.com/Websoft9/docker-library/assets/16741975/1470fbb9-f97d-498b-82fb-fb57ccf7781d)