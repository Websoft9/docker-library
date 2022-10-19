# ClamAv

扫描方案：

```
docker exec -it clamav sh
clamscan -ri /scandir --log=myscan.log
```

myscan.log 为扫描结果，如果包含 Infected files 信息，表明系统有病毒。  


## FAQ

#### ClamAV 容器没有访问宿主机文件的权限?

```
apk add sudo
sudo clamscan -r /scandir
```

#### clamscan 与 clamdscan 有什么区别？

Clamscan 比 Clamdscan 慢，因为必须启动该进程并为传递给它的每个文件重新加载病毒数据库。

#### 扫描显示 Infected files 但没有具体信息？

需通过 --log 参数将日志输出到文件，然后通过文件寻找 
