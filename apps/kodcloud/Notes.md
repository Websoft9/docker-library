## FAQ

#### 除了dockerhub和githuab，那有哪些免费的镜像发布平台？

云平台可免费公开发布docker镜像，通过个人账号上传了一个测试镜像
```
docker pull registry.cn-hongkong.aliyuncs.com/docker-services/discuzq
```

#### ENTRYPOINT和CMD在哪些情况下会运行其中命令或脚本？

容器不管是初次启动或重启的时候，cmd和enterpoint都会执行

#### ENTRYPOINT和CMD和Dockefile的关系以及如何使用？

shell模式和exec模式
shell模式: 启动shell命令模式，如bash，sh。shell模式下的环境变量可用，如$PATH
exec模式: 单独的进程运行模式，没有环境变量。["echo","1111"]也会报错，因为不知道echo命令，可以采用["/bin/echo","1111"];或者把shell单做一个可执行程序["bash","-c","echo 1111"]`

ENTRYPOINT ["executable", "param1", "param2"] exec执行模式   a  
ENTRYPOINT command param1 param2  shell执行模式   b  

CMD ["executable","param1","param2"] 单独执行模式 c  
CMD ["param1","param2"] 和enterpoint联用模式,不能单独存在 d  
CMD command param1 param2  shell执行模式 e  

解释：
 - 如果当dockerfile的ENTRYPOINT使用了a，你想使用cmd做额外命令时，只有作为a的参数才会起作用，就是说只能使用d。譬如即使你command使用定义 ["echo", "1111",">>","/tmp/test1"] 该命令无法执行
 - 如果当dockerfile的ENTRYPOINT使用了b，即使你启动容器时用command命令，那也不会起任何作用
 - 如果dockerfile 没有ENTRYPOINT，只有CMD。不管使用c或 e,这个时候你在docker-compose文件可以用 c和 e来覆盖启动命令


如何让容器启动命令只执行一次？  
a,容器内部解决  
HEALTHCHECK 实现容器启动后仅执行一次的模式  
b,创建别名同功能容器，临时容器追加额外操作，执行完退出，执行结果保存在数据库或持久化文件  
