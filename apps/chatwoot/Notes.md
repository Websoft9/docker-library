# Chatwoot

将官方的写法改成易读性更好的方式：

1. base 容器不需要运行
2. 弃用了 yml 文件中引用申明的方式
3. 增加了 Migrate 容器，以满足安装步骤：4) Prepare the database by running the migrations.
4. 弃用了 Redis 密码