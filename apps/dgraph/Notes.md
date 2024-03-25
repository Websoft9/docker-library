
Dgraph 是一个分布式图数据库。

## 安装

官方提供了两类镜像：

* dgraph/standalone
* dgraph/dgraph

dgraph/standalone 是用于单机使用的（默认已经启动 zero 和 alpha 两个服务），dgraph/dgraph 是用于分布式的。

分布式包括三个组件：

- zero(集群协调器)
- alpha（数据库节点）
- metal（图形化）

## Ratel 使用说明

### 测试公开的实例

1. Metal 可以先连接到官方公开的实例 https://play.dgraph.io 上，用于测试。
2. 连接成功后运行，便可以运行得到关系图
   ```
   {
    user(func: eq(name, "Alice")) {
        name
        friend {
        name
        age
        }
    }
    }
   ```

### 测试 Dgraph alpha

1. 连接到 http://InternetIP:8080 (这个 URL 不支持容器名称)
2. 无需密码即可登录

> groot 密码设置是企业版功能（ACL）


### 端口说明

在 Dgraph 中，每个 Alpha 和 Zero 节点都开放了几个不同的端口，以支持不同的通信和服务。这些端口包括：

1. **gRPC 端口**：这是 Dgraph 的主要通信端口，用于处理来自客户端的 gRPC 请求。对于 Alpha 节点，默认的 gRPC 端口是 9080。对于 Zero 节点，默认的 gRPC 端口是 5080。

2. **HTTP 端口**：这个端口用于处理来自客户端的 HTTP 请求，包括查询和突变。对于 Alpha 节点，默认的 HTTP 端口是 8080。对于 Zero 节点，默认的 HTTP 端口是 6080。

3. **内部端口**：这是用于集群内部通信的端口。这个端口是 `--my` 参数设置的端口。对于 Alpha 节点，默认的内部端口是 7080。对于 Zero 节点，默认的内部端口是 5080。

这些默认的端口可以根据需要进行更改，但你需要确保所有的 Dgraph Alpha 和 Dgraph Zero 节点都使用正确的端口，以便它们可以在集群中正确地找到并通信。  

当你在浏览器中打开 Ratel 时，它会要求你输入 Dgraph Alpha 的 HTTP 端口的 URL。


