# BT

官方在 docker hub 上提供了中文和英文两个版本的镜像：

* https://hub.docker.com/u/btpanel
* https://hub.docker.com/u/aapanel

启动进程分别为：/aapanel.sh 和 /bt.sh


## 密码问题

宝塔镜像安装后，存在默认用户名和密码，可以通过如下命令修改。  

```
# 修改默认密码
echo -e "5\nadmin123" | bt

# 修改默认用户名
echo -e "6\nadministrator" | bt
```

或
```
# 仅支持修改密码，官方未提供用户名修改方案
cd /www/server/panel && python tools.py panel $W9_PASSWORD
```

## 删除登录URI问题

```
/www/server/panel/data/admin_path.pl

```

## to do

* docker restart 后密码又被重置。仅初始化生效的改名方案参考：https://github.com/Cyberbolt/baota/blob/main/app/script.py
* configs 带入的文件没有执行权限

