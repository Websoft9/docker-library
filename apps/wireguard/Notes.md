# WireGuard

操作系统内核最低5.6。 目前已知 Ubuntu 22.04 内核为5.15

## FAQ

#### 客户端用什么？

[TunSafe](https://tunsafe.com/)

#### 客户端如何连接服务端？

1. 下载服务端生成的 peer1.conf 文件（位于存储目录下的 peer1 文件夹）
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


