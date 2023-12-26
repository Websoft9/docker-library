# MySQL

This application is based on Official image, and user can add:

- extra configure file
- extra sql file

## FAQ

#### MySQL 容器为什么无法使用 172.0.0.1 这种访问方式？

暂时无法得知，可能与用户的所支持的主机名列表有关系

#### command 能带哪些参数？

运行下面的命令查询  
```
docker run -it --rm mysql:tag --verbose --help
```
