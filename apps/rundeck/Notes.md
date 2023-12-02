# Rundesk

It can running, but have below problem:

- Is there environment for Rundesk administrator username or password?
- Is there have runner for Rundesk opensource?

官方文档看似给出了配置文件与环境变量之间的对应关系，但目前还没有搞明白

## FAQ

#### When login sucesss, the URL redirect http://IP:9098/IP:9098/menu/home?

RUNDECK_GRAILS_URL must have http or https:
```
RUNDECK_GRAILS_URL=http://IP
```
