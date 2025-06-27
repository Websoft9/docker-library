# crowdsec

## 一、crowdsec基础使用教程：

crowdsec软件负责检测恶意流量，查看列表，可以手动封禁ip。

基本命令：

| 命令示例                                                     | 含义                                                         |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| cscli collections list                                       | 列出已安装的规则集合。（安装新规则：cscli collections install crowdsecurity/sshd） |
| cscli parsers list                                           | 列出日志解析器                                               |
| cscli decisions list                                         | 查看封禁列表。                                               |
| cscli decisions add --ip 192.168.121.14 --duration 24h       | 手动封禁IP为192.168.121.14，封禁时间24小时。（--reason <封禁原因>） |
| cscli decisions delete --ip 192.168.121.14                   | 解除封禁IP为192.168.121.14。                                 |
| cscli allowlists create my_allowlist --description "test allowlist" | 创建允许列表。                                               |
| cscli allowlist add my_allowlist 192.168.121.14 -e 7d        | 将IP为192.168.121.14加入允许列表。（默认情况下，允许列表条目没有过期时间，但可以使用 -e 指定有效期，-d 添加描述） |
| cscli allowlist inspect my_allowlist                         | 查看允许列表。                                               |
| cscli allowlists remove my_allowlist 192.168.121.14          | 删除允许列表的条目。                                         |
| cscli allowlists delete my_allowlist                         | 删除该允许列表。                                             |

更多详细命令可查阅官方文档：https://doc.crowdsec.net/docs/

## 二、crowdsec-firewall-bouncer工具

若需要自动封禁，需要额外安装crowdsec-firewall-bouncer工具。

示例：

```
# 生成布防器 API 密钥（在 CrowdSec 容器内执行）
docker exec -it crowdsec cscli bouncers add firewall-bouncer --key-random

# 启动防火墙布防器
docker run -d \
  --name crowdsec-firewall-bouncer \
  --network host \
  -v /etc/crowdsec/bouncers:/etc/crowdsec/bouncers \
  -e BOUNCER_API_KEY="YOUR_GENERATED_API_KEY" \
  -e FIREWALL_MODE="nftables" \
  crowdsecurity/crowdsec-firewall-bouncer:latest
```

## 三、crowdsec控制台使用教程：

1、安装好后去官网注册一个账号：https://app.crowdsec.net/security-engines

2、账号首页最下面有一个密钥注册命令，类似：sudo cscli console enroll -e context <your_key>

3、复制去容器内部执行，执行后在官网就会出现对应的控制台。