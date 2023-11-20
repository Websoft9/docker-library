# WireGuard

本项目仅是 WireGuard 的运行方案，供内部技术研究之用途。

> 私自搭建 VPN 甚至制售 VPN 有可能涉嫌为非法犯罪。使用未经许可的VPN服务访问被屏蔽的网络资源是违法行为，可能会面临相应的处罚。您可以选择合法注册的VPN服务提供商，并遵守中国的网络法规。

操作系统内核最低5.6。 目前已知 Ubuntu 22.04 内核为5.15
本软件需经常更换端口，才能正常使用，其具体原因无法得知  

快捷运行：bash getkeys.sh，会将 keys 拷贝到 /data/keys

## FAQ

#### Wireguard 端口是什么协议？

UDP

#### 客户端用什么？

[TunSafe](https://tunsafe.com/)

#### 客户端如何连接服务端？

1. 下载服务端生成的 peer*.conf 文件（位于工作目录下 config 文件夹）
2. 本地客户端导入这个配置文件后，对 Address 稍加修正（ip后追加"/24"）
   ```
   [Interface]
    Address = 192.168.2.2/24
    PrivateKey = OJ42/BLqDZLcqs+b/PHBAU76m86Jf/hzcXQ=
    ListenPort = 51820
    DNS = 192.168.2.1

    [Peer]
    PublicKey = mQq0xwKtm+TO1ImLKxUho=
    PresharedKey = k0HuM3ahmhJ5cQCH9Zo=
    Endpoint = 47.222.3.236:51820
    AllowedIPs = 0.0.0.0/0
   ```
 3. 连接

#### 一个隧道（Peer）是否可以多人使用？

不可以，需通过修改环境变量 PEERS 更改数量

#### 如何增加更多隧道？

更改 PEERS 的值即可

参考：https://github.com/linuxserver/docker-wireguard

#### Peer.conf 文件中的 Address 需要与本地电脑 IP 一致吗？

不需要

#### 网络畅通仍然连不上？

更换 W9_UDP_PORT 试试
