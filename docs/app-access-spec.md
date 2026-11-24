# App Access Spec

| 属性 | 内容 |
| --- | --- |
| 状态 | 146 个活跃应用的默认配置已迁移到 V2 声明并纳入静态门禁；静态校验不代表运行态验收。非同拓扑的手动变体和下游 Websoft9 消费见第 4、9 节 |
| 适用范围 | 应用包的 `variables.json.access`、`docker-compose.yml` 端口映射与 `.env` 地址/端口变量 |
| 目的 | 以单一 `access` 声明驱动安装端口配置、逻辑入口识别、安装期与运行期多域名绑定及应用原生地址同步，逐步移除平台自定义端口与 URL 变量 |

## 1. 目标与职责边界

`variables.json.access` 是应用对外网络端口、逻辑访问入口与应用内部外部地址注入目标的单一静态声明（DSL）。一份声明同时覆盖四条链路：

1. **安装时端口控制**：声明哪些服务端口默认开放宿主机映射（`public: true`）、哪些默认关闭按需开放（`public: false`）；纯内部依赖端口不声明、不开放。
2. **逻辑访问入口**：声明端口上承载的界面、API 与客户端直连入口（`endpoints`），供访问面板按用途分组展示与协议识别。初始化凭据提取（日志、文件、CLI）与首次登录说明继续由同级 `credentials` 与 `help.login` 独立承担（旧中间态 `setup` 已废弃清理）。
3. **安装时与安装后域名绑定**：识别可绑定 HTTP(S) 域名的服务端口组，支持单域名、同一端口组多域名（主域名 + 别名域名）以及多服务端口组各自独立绑定域名。
4. **应用内部地址与映射端口同步**：按需声明原生环境变量名数组（`rootUrl`、`host`、`mappedPort`），将实例最终生效的主地址或宿主机映射端口精确写入 `.env`，替代旧版 `W9_URL`、`W9_URL_REPLACE`、`W9_URL_WITH_PORT` 与 `W9_*_PORT_SET`。

### 文件与运行态职责划分

| 位置 | 保留与承担的职责 | 不再承担的内容 |
| --- | --- | --- |
| `variables.json.access` | 服务目标端口、传输协议、默认发布开关、强制域名/HTTPS 约束、逻辑访问入口、需同步地址/映射端口的原生变量名 | 实例实际域名、实际宿主机端口、TLS 证书、实时容器可达状态、初始化凭据提取 |
| `docker-compose.yml` | 服务拓扑、容器固定监听端口、原生配置引用，以及脱离平台手动执行 `docker compose up` 所需的默认端口映射 | `${W9_*_PORT_SET}` 宿主端口占位符、`W9_URL` 平台变量透传、`hostname: ${W9_URL}` |
| `.env` | 应用原生环境变量与单机默认运行值（本阶段保留 `W9_ID`、`W9_NETWORK`、`W9_REPO`、`W9_DIST`、`W9_VERSION`、`W9_DB_EXPOSE`、`W9_DB_VERSION`、`W9_LOGIN_USER`、`W9_LOGIN_PASSWORD`、`W9_POWER_PASSWORD` 及非端口业务输入如 `W9_DEEPSEEK_API_KEY_SET`） | `W9_*_PORT_SET`、`W9_HTTP_PORT`、`W9_HTTPS_PORT`、`W9_DB_PORT`、`W9_API_PORT`、`W9_URL`、`W9_URL_REPLACE`、`W9_URL_WITH_PORT`、`W9_ADMIN_PATH` |
| 消费端实例配置 | 用户实际的端口开放开关、自定义宿主机端口、已绑定域名列表、选定的主域名与证书配置 | 不回写应用模板 `variables.json` |

内部数据库依赖继续使用独立的 `database` 契约（见 [docs/app-database-connection-spec.md](app-database-connection-spec.md)），不混入 `access`。

---

## 2. 声明结构

`access` 为顶层有序数组，按 **`(service, port, protocol)`** 组织端口组；不设外层 `entries` 包装，不拆分顶层 `ports` 或 `public_url`。

```json
{
  "access": [
    {
      "id": "http",
      "service": "wordpress",
      "port": 80,
      "public": true,
      "rootUrl": ["WP_HOME", "WP_SITEURL"],
      "endpoints": [
        {"roles": ["web"], "scheme": "http"},
        {"roles": ["admin"], "scheme": "http", "path": "/wp-admin"}
      ]
    }
  ]
}
```

明确没有任何对外网络端口与访问入口的工具类应用（如 FFmpeg），声明空数组；缺失 `access` 表示未声明、能力未知，阻塞校验与发布：

```json
{
  "access": []
}
```

### 2.1 端口组字段（`access[]`）

| 字段 | 必填 | 类型 | 规则与语义 |
| --- | --- | --- | --- |
| `id` | 是 | `string` | 应用内唯一稳定标识，匹配 `^[a-z][a-z0-9-]*$`；供实例端口配置、域名绑定与网关自定义配置持久化引用，不得由 `roles` 动态推导 |
| `service` | 是 | `string` | `docker-compose.yml` 中的默认激活常驻服务名，必须存在于 `services`；不含一次性 `init` 容器或默认未启用的互斥 `profiles` 服务 |
| `port` | 是 | `integer \| string` | 容器内部目标监听端口（整数 `1–65535`）；确由应用原生环境变量驱动监听端口时允许单变量引用 `"${VAR}"`（不含默认值表达式），严禁填宿主机端口 |
| `protocol` | 否 | `"tcp" \| "udp"` | 传输层协议，省略时默认为 `"tcp"`；UDP 端口必须显式声明 `"udp"`，与应用层 `scheme` 分离 |
| `public` | 是 | `boolean` | 宿主机端口映射的**默认开关**。`true` 表示默认发布到宿主机；`false` 表示默认不发布到宿主机（安装或运行期可按需开启，且不影响容器内网反代） |
| `requireDomain` | 否 | `boolean` | 省略时默认为 `false`。设为 `true` 时表示该端口组不支持裸 IP 直连，**安装时必须绑定至少一个域名**，且运行期禁止删空最后一个绑定域名（如 Jitsi、Teleport、Vaultwarden）；仅含 `http`/`https`/`ws`/`wss` 入口的端口组可声明 |
| `requireHttps` | 否 | `boolean` | 省略时默认为 `false`。设为 `true` 时表示浏览器外部访问**必须强制使用 HTTPS / WSS**（自动申请/挂载内置兜底证书并开启 `ssl_forced=true`，禁止纯 HTTP/WS 访问）。若组内 `endpoints` 已存在 `scheme` 为 `"https"` 或 `"wss"`，默认自动强制外部 TLS，无需重复声明；专门用于容器内监听明文 `http`/`ws` 但客户端要求安全上下文的应用（如 Vaultwarden）；仅含 `http`/`https`/`ws`/`wss` 入口的端口组可声明 |
| `rootUrl` | 否 | `string[]` | 非空、无重复的原生环境变量名数组。将该端口组生效的唯一完整主地址（含公网协议、主机及必要端口，**不含尾斜杠**，如 `https://app.example.com` 或 `http://192.0.2.10:9001`）写入所列变量；仅含 `http`/`https`/`ws`/`wss` 入口的端口组可声明 |
| `host` | 否 | `string[]` | 非空、无重复的原生环境变量名数组。HTTP(S) 端口组写入浏览器 `Host` 形式（域名模式如 `app.example.com`，IP 直连含非标端口如 `192.0.2.10:9001`）；SSH 等非 HTTP 端口组写入纯主机名或 IP（不含端口）。**严禁将 `host` / `rootUrl` 变量用于 Compose 的容器 `hostname:`** |
| `mappedPort` | 否 | `string[]` | 非空、无重复的原生环境变量名数组。将该端口组生效的宿主机映射端口号（如 `"2222"`）写入容器内部所列配置变量，用于需感知映射端口的应用（如 GitLab / Gitea SSH） |
| `endpoints` | 是 | `array` | 该端口承载的逻辑访问入口有序数组；无应用层入口的纯传输或待配置采集端口声明 `[]` |

### 2.2 逻辑入口字段（`endpoints[]`）

端口发布与域名绑定均关联到端口组 `id`，不再设入口级 `primary` 或入口级 `id`。

| 字段 | 必填 | 类型 | 规则与语义 |
| --- | --- | --- | --- |
| `roles` | 是 | `string[]` | 非空、无重复，命中 `metadata/access-types.json` 角色字典；按 `ui → api → infra` 顺序排列 |
| `scheme` | 是 | `string` | 容器监听的应用层协议，命中协议字典且被该入口所有 `roles` 允许；不代表公网域名协议 |
| `path` | 否 | `string` | 访问路径，省略时默认为 `"/"`；必须以 `/` 开头，不含 origin、凭据、`?` 或 `#`；仅 `allowPathQuery: true` 的协议允许 |
| `query` | 否 | `object` | 静态公开查询参数（字符串键值对象），仅 `allowPathQuery: true` 的协议允许；禁止包含凭据、token 或模板占位符 |

### 2.3 唯一性、排序与组合约束

- **数组优先级排序（主域名绑定目标）**：`access` 为有序数组，数组顺序即优先级，不设顶层 `primary` 或主容器字段。安装界面的**主域名**默认绑定至推荐集合中的第一个端口组（推荐规则见第 9.5 节）；若应用不含任何 `ui` 类角色，则取第一个含 `http`/`https`/`ws`/`wss` 入口的端口组；排在其前但只有 `ssh`、`grpc`、`amqp`、`bolt` 或空 `endpoints` 的端口组不参与该选择。非推荐的可绑域名端口组默认不绑定域名，可在安装高级项或安装后手动开启。
- **首位端口组的判定口径**：首位必须是用户装完后**用浏览器直接打开就有内容**的端口组，按以下顺序判定：
  1. 可浏览界面（`ui` 类角色，如 `web`、`admin`、`dashboard`、`notebook`、`remote-desktop`）优先；
  2. 多个 `ui` 时，取用户日常最常打开的主界面（如 Kong 的 Kong Manager、Traefik 的 dashboard），而非仅承载转发、打开即空响应或 JSON 错误的管理 API／业务网关端口；
  3. 无任何 `ui` 角色时，取面向业务的 `api`／`gateway` 端口组；
  4. 纯转发端口（如 Kong 的 `8000`、Traefik 的 `80`）和无界面应用的 API 端口，默认域名绑定价值有限，应排在管理界面之后，由用户在高级项或安装后按需绑定业务域名。
- **端口组唯一**：同一应用内 `(service, resolved_port, protocol)` 必须唯一；同一端口号的 TCP 与 UDP（如 `5140/tcp` 与 `5140/udp`）须拆分为两个独立端口组。
- **组内入口唯一**：同一端口组内 `(scheme, path, query)` 必须唯一（比较时缺省 `path` 为 `"/"`、缺省 `query` 为 `{}`，键顺序无关）；相同访问目标的多重用途合并到同一入口的 `roles` 中。
- **写入变量无冲突**：同一环境变量名不得同时出现在多个端口组的 `rootUrl`、`host` 或 `mappedPort` 中，也不得在同一端口组的 `rootUrl`、`host`、`mappedPort` 之间重复出现。

---

## 3. 角色与协议字典

`metadata/access-types.json` 是角色（`roles`）与应用层协议（`schemes`）的唯一机器规则来源。传输层 `protocol`（`tcp` / `udp`）在端口组上表达，不混入应用层 `schemes` 字典。

| 角色 | `kind` | 允许的 `scheme` |
| --- | --- | --- |
| `web`、`admin`、`dashboard`、`notebook`、`remote-desktop` | `ui` | `http`、`https` |
| `api` | `api` | `http`、`https`、`grpc`、`grpcs`、`ws`、`wss` |
| `metrics` | `api` | `http`、`https` |
| `gateway` | `api` | `http`、`https`、`ws`、`wss` |
| `db` | `infra` | `http`、`https`、`grpc`、`grpcs`、`mysql`、`postgresql`、`mongodb`、`rethinkdb`、`redis`、`mssql`、`oracle`、`bolt` |
| `mq` | `infra` | `amqp`、`kafka`、`stomp`、`openwire` |
| `ssh` | `infra` | `ssh` |

19 项应用层协议的地址形态与路径能力：

| `scheme` | `address` | `allowPathQuery` |
| --- | --- | --- |
| `http`、`https`、`ws`、`wss` | `url`（完整 URL） | `true` |
| `grpc`、`grpcs`、`ssh`、`mysql`、`postgresql`、`mongodb`、`rethinkdb`、`redis`、`mssql`、`oracle`、`bolt`、`amqp`、`kafka`、`stomp`、`openwire` | `hostport`（主机与端口并标注协议） | `false` |

`kind`（`ui` / `api` / `infra`）仅用于界面按用途分组与检索，不决定协议类型或域名绑定资格；入口展示主分组取首个角色的 `kind`。

---

## 4. 端口分类与 `.env` / `docker-compose.yml` 改造规范

### 4.1 三类容器端口处理准则

| 端口类别 | 典型场景 | `access` 声明 | 仓库 `docker-compose.yml` | 安装界面行为 |
| --- | --- | --- | --- | --- |
| **纯内部依赖端口** | Web 应用自带的 `mysql:3306`、`redis:6379`、内部 worker 端口 | **不声明** | 保持上游原样（上游本就不发布宿主机端口） | 不展示，禁止用户误开内部依赖端口 |
| **默认开放端口** | 主 Web 端口 `80`、数据库产品服务端口 `5432`、Git SSH `22` | 声明，`"public": true` | 保持上游/官方 `ports` 映射（如 `"9001:80"`、`"5140:5140/udp"`） | 开关默认开启，外部端口输入框默认取 Compose 映射左侧端口 |
| **按需开放端口** | RabbitMQ `4369`、Graylog 采集端口 | 声明，`"public": false` | **同样保持上游 `ports` 原样，不为 `public` 改写 compose** | 开关默认关闭；用户开启时才生成宿主机映射 |

`variables.json` 是访问策略的唯一 DSL，`docker-compose.yml` 尽量保持上游原样：`public` 只表达「平台安装与部署时的默认发布行为」，与仓库 compose 是否写了 `ports` 无关。消费端部署实例时按 `public` 生成 override：`true` 保留映射，`false` 移除映射；直接 `docker compose up` 会按仓库 `ports` 原样暴露，属于单机自测行为，不代表平台默认。

`access` 声明的端口必须在目标服务的 `ports` 或 `expose` 中有监听证据；`public` 是平台默认发布策略，不要求与仓库 compose 的映射一致。若某个端口的宿主机映射、容器监听与应用对外通告必须取**同一个值**（例如 Jitsi JVB 的 WebRTC UDP 媒体端口），应声明为 `protocol: "udp"` 的 `access` 端口组：`port` 引用该变量、`endpoints` 为空、`mappedPort` 列出同一变量，使 Compose 的 `- "${JVB_PORT}:${JVB_PORT}/udp"`、容器内监听与 SDP 通告保持三方一致，用户仍可在安装时修改。只有确实无法由用户配置、且不属于任何访问入口的固定传输端口，才在服务上用 `x-websoft9-unmanaged-ports` 明确列出，键为容器 `port/protocol`，值为豁免原因。部署保留其原始映射并考虑冲突，不把它当作域名或入口；若固定宿主端口已被占用，需先释放它，不能盲目自动改号。

`access` 描述默认 Compose 拓扑；不同监听端口、协议或入口的版本不能只作为镜像标签列入同一商店包。尚未支持按版本选择声明时，把这类变体作为手动 Compose 文件交付并记录启动方法（如 InfluxDB 3 Core），不使用默认声明发布它。

### 4.2 `public` 默认值判定规则

安装目标只有一个：**装完立刻能用**。安装界面不应预设一堆需要额外配置才有意义的端口，也不应为了"以后可能要用"扩大公网暴露面和安全组放通范围。装完后用户随时可以在「我的应用 → 访问」中开启任何已声明但默认关闭的端口，因此默认值按「装完是否需要立即可用」判定，而不是按「技术上能不能访问」判定。

**`public: true` — 满足任一条件才允许**

1. 该端口组是应用的主浏览器界面（`endpoints` 含 `kind == ui` 的角色，如 `web`、`admin`、`dashboard`、`notebook`、`remote-desktop`）；
2. 该端口组是数据库 / 缓存 / 消息队列 / 搜索 / 向量产品**自身的主服务端口**（PostgreSQL `5432`、MySQL `3306`、Redis `6379`、MongoDB `27017`、RabbitMQ `5672`、Kafka `9092`、Elasticsearch `9200` 等）；
3. 该端口组是应用核心功能在安装后**立即必需**且只能由外部直连的端口（GitLab / Gitea / Jihu 的 SSH、Kong / Traefik 的主代理端口、Jitsi JVB 的 WebRTC 媒体端口）。

**`public: false` — 出现任一情形必须关闭**

1. 采集或接收类辅助端口（Graylog 的 `beats` / `syslog-*` / `raw-*` / `gelf-*` / `forwarder-*`、Wazuh 的 `agent` / `enrollment`）；
2. 需要用户在应用内先完成配置才生效的端口（先创建 Input、先启用插件、先绑定 Agent、先部署应用包）；
3. 内部协调、集群或调试端口（RabbitMQ `epmd` `4369`、Erlang 分布式端口、内部 Bridge 端口）；
4. 监控指标端口（`metrics`）；
5. 次要或维护入口（`novnc`、`tensorboard`、`deployment` 部署 API）。

**一句话自查**

| 判断 | 结论 |
| --- | --- |
| 用户装完、不做任何配置就会访问它 | `true` |
| 必须先做另一件事它才有意义 | `false` |
| 打开它只是多暴露一个端口给公网和安全组 | `false` |

**与 `docker-compose.yml` 的关系**

`variables.json` 只表达意图，不要求为了 `public` 去改动上游 compose：

- 仓库 `docker-compose.yml` 保持上游/官方原样，包括它自带的 `ports` 映射；
- `public: true` 表示消费端部署时**保留**该映射，`public: false` 表示部署时**生成 override 移除**该映射；
- `libs app-check` 只校验 `(service, port, protocol)` 在目标服务的 `ports` 或 `expose` 中有监听证据，不再要求 `public` 与仓库映射一致；
- 直接 `docker compose up` 会按仓库 `ports` 原样暴露端口，这是单机自测行为，不代表平台默认。

**例外**：`requireDomain: true` 且 `public: false` 的端口组，必须确认其入口能通过绑定域名或容器网络交付（如 Vaultwarden 的明文 `80` 仅经 TLS 网关访问）。

### 4.2 平台变量移除与替代规则

1. **移除 `W9_*_PORT_SET`（保留非端口类业务输入 `_SET`）**
   - `.env` 删除全部 `*_PORT_SET` 端口映射变量；非端口类业务安装输入（如 `W9_DEEPSEEK_API_KEY_SET`、`W9_KAFKA_BROKERS_SET`）本阶段保留不动。
   - 仓库 `docker-compose.yml` 的 `ports` 直接使用字面默认映射（如 `"9001:80"`）；容器内部监听端口固定（如 `80`、`3000`、`22`），不得用同一个变量同时绑定宿主机端口和容器内部监听端口。
   - 仅当上游应用需要在容器内部配置中感知宿主机映射端口（如 Git 克隆地址中的 SSH 端口）时，保留应用原生端口变量并在端口组声明 `mappedPort`。
2. **移除冗余内部端口常量（`W9_HTTP_PORT`、`W9_HTTPS_PORT`、`W9_DB_PORT`、`W9_API_PORT`）**
   - 未被容器配置或脚本实际引用的冗余定义全部删除。
   - 源码运行时应用（遵循 [docs/runtime-app-spec.md](runtime-app-spec.md)）或自定义启动脚本确需动态监听端口时，改用应用原生端口变量（如 `PORT`、`APP_PORT`），并在 `access[].port` 中引用该原生变量（如 `"${PORT}"`）。
3. **移除 `W9_ADMIN_PATH` 与拼接旧地址的提示变量**
   - 后台或控制台路径统一在对应端口组的 `endpoints[].path`（如 `"/wp-admin"`）中声明，不在 `.env` 中重复维护；拼接了 `W9_URL` / `*_PORT_SET` 的连接提示变量（如 `W9_LOGIN_ConnectURL`）一并移除，交由 `access` 入口统一展示。
4. **移除 `W9_URL`、`W9_URL_REPLACE` 与 `W9_URL_WITH_PORT`**
   - **无需感知外部地址的应用**（如 Portainer、Prometheus、RedisInsight）：直接删除上述变量，不新增任何替代变量；是否支持域名绑定完全由端口组是否含 `http`/`https`/`ws`/`wss` 入口决定。
   - **需要完整外部 URL 的应用**：在 `.env` 中定义应用原生变量并给出合法默认示例值（如 `NEXTAUTH_URL=http://localhost:9001`），在对应端口组声明 `"rootUrl": ["NEXTAUTH_URL"]`。
   - **需要不含协议头外部地址的应用**（如 `CANVAS_HOST`、`PS_DOMAIN`、`SETTING_EXTERNAL_HOST`、`DSH_TRUSTED_HOSTS`）：在 `.env` 定义原生变量，并在对应端口组声明 `"host": ["..."]`。严禁把外部地址变量赋给 Compose 的 `hostname:`（IP 直连时含 `:port` 会导致容器因非法主机名启动失败）。
   - **需要固定路径后缀或强制尾斜杠的变量**：`rootUrl` 始终输出不带尾斜杠的基础地址；带后缀或尾斜杠的变量通过 `.env` 或 `docker-compose.yml` 原生变量展开拼接（如 `API_EXTERNAL_URL=${SUPABASE_PUBLIC_URL}/auth/v1`、`GRAYLOG_HTTP_EXTERNAL_URI=${GRAYLOG_EXTERNAL_URL}/`），不在 `access` 中引入模板拼接语法。
   - **与当前应用入口无关的外部站点变量**（如指向外部前端业务的跳转地址）：作为普通应用环境变量保留，不纳入 `access`。
   - **包内脚本同步改造**：`src/` 下的入口脚本、PHP 钩子或配置模板必须同步改为读取上述应用原生变量，不得残留 `W9_URL` 读取。

### 4.3 与 `env.first_startup_only` 及网关自定义配置的配合

- **首次启动固化地址（`env.first_startup_only`）**：若应用将 `rootUrl` 或 `host` 中的变量同时列在 `variables.json` 的 `env.first_startup_only` 中（如首次安装写入持久化配置文件后不再读取环境变量的应用），除非包内启动脚本已实现每次启动同步，否则该变量仅在安装首次启动前写入生效；运行期消费端应禁用一键修改主地址变量（或明确提示需进入应用后台修改配置），避免改了 `.env` 却不生效的“假切换”。
- **网关自定义反代配置（`src/nginx-proxy*.conf`）**：单个可绑域名 HTTP 端口组的应用继续使用 `src/nginx-proxy.conf`；含多个可绑域名 HTTP 端口组的应用（如 Kong）支持按端口组 `id` 提供 `src/nginx-proxy-<id>.conf`，优先匹配对应端口组配置，禁止跨端口组硬编码转发端口。

---

## 5. 域名绑定、多域名与主地址生命周期

### 5.1 域名候选判定、绑定次数与反代目标

- **候选规则**：端口组 `endpoints` 中只要存在至少一项 `scheme` 为 **`http`、`https`、`ws` 或 `wss`**（即字典中 `allowPathQuery: true` 的全部 URL 类协议），该端口组即可绑定域名——**不限制 `roles` 或 `kind`**（无论是 `web`、`admin`、`api`、`gateway` 还是提供 HTTP 接口的 `db` 均可绑定域名，网关反代默认开启 WebSocket Upgrade 支持）。
- **与宿主机端口发布解耦**：网关反代通过容器网络直连实例的 `(service, port)`，**不要求 `public: true`**；用户可在关闭宿主机端口映射的同时通过域名安全访问应用。
- **绑定粒度（绑一次 vs 绑多次）**：域名绑定挂载在端口组 `id` 上：
  - **同端口多路径（绑一次共享）**：同一端口组下的多个 `endpoints`（如 WordPress 的 `/` 与 `/wp-admin`，或 Graylog 的 `/` 与 `/api/`）只需对该端口组绑定一次域名，所有入口路径天然共用该组域名；`endpoints[].path` 仅用于生成访问快捷链接，不代表反代路径重写规则。
  - **不同端口/不同服务（各自独立绑定）**：位于不同端口组的服务（如 OpenSearch 的 `5601` 界面与 `9200` API，或 Kong 的 `8002` 管理界面、`8001` 管理 API 与 `8000` 业务网关）无法靠同一域名根路径区分，需为各端口组分别绑定独立域名；安装期只为**推荐集合**（含 `ui` 类角色的端口组；应用无 UI 时取首个候选组）生成默认域名并默认启用，其余候选组默认不绑定，可在高级项或安装后手动开启，详见第 9.5 节。
- **协议独立与强制 HTTPS**：容器上游 `scheme` 为 `"http"` 或 `"ws"` 可绑定公网 HTTPS/WSS 域名；写入 `rootUrl` 的协议取公网实际访问协议（例如 `http` 入口绑定 HTTPS 证书输出 `https://...`，纯 `ws` 入口绑定 HTTPS 证书输出 `wss://...`）。当组内入口存在 `scheme` 为 `"https"` / `"wss"` **或**端口组显式声明 `requireHttps: true` 时，反代对内仍按实际容器监听协议（`https` 用于 `https`/`wss`，`http` 用于 `http`/`ws`）转发，对外域名必须强制启用 TLS 证书（未选证书时自动申请或挂载内置自签证书兜底）并开启 HTTP 强跳 HTTPS（`ssl_forced=true`），禁止创建纯明文域名。
- **强制绑定域名（`requireDomain: true`）**：声明 `requireDomain: true` 的端口组在安装界面将域名设为必填项，禁止裸 IP 安装；运行期删除域名时必须保留至少一个有效域名。
- **禁止发布需要 TLS 的明文入口**：`requireHttps: true` 若用于容器内明文监听器，必须声明 `public: false`，消费端也不得开启该明文直连映射；应通过 TLS 网关交付。`requireDomain` 本身不禁止发布已经使用 TLS 的监听器。

### 5.2 安装时绑定 vs 安装后多域名管理

`rootUrl` / `host` 的存在性直接替代原 `W9_URL_REPLACE` 的全部控制语义：

| 场景 | 未声明 `rootUrl` / `host` 的端口组 | 声明了 `rootUrl` / `host` 的端口组 |
| --- | --- | --- |
| **安装时** | 可选填 1 个或多个域名，全部作为平级反代域名创建；不改写 `.env` 地址变量 | 可填 1 个或多个域名（多域名时指定 1 个主域名）；未填域名时按宿主直连生成 `http(s)://<host>:<published_port>`。首次启动前即写入目标原生变量，确保依赖首次初始化地址的应用一次启动成型 |
| **多域名界面能力** | 所有已绑定域名平级展示，**不显示“设为主域名”** | 在已绑定域名列表中标识当前主域名，支持一键切换主域名（辅助域名作为反代别名保留；上游应用是否将别名重定向回主域名取决于应用自身机制） |
| **安装后增删别名域名** | 仅更新网关反代配置，**不改 `.env`、不重建容器** | 只要当前主域名未变且协议未变，仅更新网关反代配置，**不改 `.env`、不重建容器** |
| **安装后切换主域名 / 主域名切 HTTPS / 删除主域名** | 仅更新网关反代配置，**不改 `.env`、不重建容器** | 若删除原主域名，须提升剩余域名之一为主域名（无剩余域名且已开启宿主机端口时回退为宿主直连地址）；按变量名键值精确更新 `.env` 目标变量并执行 `docker compose up -d` 重建生效 |

---

## 6. 安装与运行稳定性硬约束

消费端实现与本库校验门禁必须共同遵守以下四条防线：

1. **外部地址与强制域名非空约束**：凡声明了 `requireDomain: true` 的端口组，安装与运行全周期必须绑定至少一个域名；凡声明了 `rootUrl` 或 `host`（且未设 `requireDomain: true`）的端口组，实例在任一时刻必须满足**“开启宿主机端口映射”或“绑定至少一个域名”**至少其一。禁止因无可用访问入口而向目标环境变量写入空值导致容器崩溃。
2. **关闭端口映射不清空 `mappedPort`**：当声明了 `mappedPort` 的端口组（如 GitLab SSH）被用户关闭宿主机映射时，部署层仅移除对应的 Compose `ports` 映射，**保留 `.env` 中目标变量的默认端口号不变**，严禁写入空字符串破坏容器内配置文件语法。
3. **受管端口映射整组替换**：Docker Compose 多文件合并默认对 `ports` 列表执行追加而非覆盖。实例部署生成配置时必须整组替换受管服务的 `ports`（或使用受支持的 `!override` / `!reset`），确保关闭 `public` 时宿主机不再监听该端口，并以 Docker 实际 `PortBindings` 作为运行态直连地址依据。
4. **精确键值更新与静态残留拦截**：消费端更新 `.env` 中的 `rootUrl`、`host`、`mappedPort` 目标变量时，必须按变量名解析并精确替换对应键值，严禁对 `.env` 全文做旧值字符串替换。本库校验门禁拦截已迁移包中任何残留的 `W9_*_PORT_SET`、`W9_HTTP_PORT`、`W9_HTTPS_PORT`、`W9_DB_PORT`、`W9_API_PORT`、`W9_URL`、`W9_URL_REPLACE`、`W9_URL_WITH_PORT`、`W9_ADMIN_PATH` 引用，并校验 `public: true` 与仓库默认 `docker-compose.yml` 端口映射一致。

---

## 7. 安全规则

- `endpoints[].path` 必须以 `/` 开头，拒绝控制字符、反斜杠、非法百分号编码、`//host` 网络路径引用，以及字面或百分号编码的 `.`、`..` 路径段。
- `endpoints[].query` 键值拒绝控制字符与模板占位符；键名忽略大小写拒绝 `token`、`access_token`、`password`、`secret`、`api_key`、`authorization` 等敏感凭据字段，其余参数须人工确认为公开静态参数。动态一次性初始化令牌（如从容器日志提取的 `token`）通过 `credentials` 读取展示，严禁写入静态 `query`。
- 消费端须使用标准 URL API 拼接实例基础地址、`path` 与 `query`，校验生成结果的 origin 与实例配置一致。

---

## 8. 不同复杂度应用完整示例

以下示例展示完整的新版 `access` 声明以及对应的 `.env` / `docker-compose.yml` 配合方式。

### 8.1 无网络入口应用（FFmpeg）

```json
{
  "access": []
}
```

### 8.2 单端口、多路径、多域名共享主地址（WordPress）

- `variables.json`：

```json
{
  "access": [
    {
      "id": "http",
      "service": "wordpress",
      "port": 80,
      "public": true,
      "rootUrl": ["WP_HOME", "WP_SITEURL"],
      "endpoints": [
        {"roles": ["web"], "scheme": "http"},
        {"roles": ["admin"], "scheme": "http", "path": "/wp-admin"}
      ]
    }
  ]
}
```

- `.env` 与 `docker-compose.yml` 配合：
  - `.env` 移除 `W9_HTTP_PORT`、`W9_HTTP_PORT_SET`、`W9_URL`、`W9_URL_REPLACE`，保留原生 `WP_HOME=http://localhost:9001` 与 `WP_SITEURL=http://localhost:9001`。
  - `docker-compose.yml` 将 `ports` 改为 `["9001:80"]`，移除 `W9_URL` / `W9_URL_REPLACE` 环境变量注入；包内 `src/websoft9-url.php` 改为直接读取 `WP_HOME` / `WP_SITEURL`。
  - 绑定多个域名时，`/` 与 `/wp-admin` 共享同一端口组绑定，仅选定的主域名写入 `WP_HOME` 和 `WP_SITEURL`。

### 8.3 Web/API 尾斜杠拼接 + 多 TCP/UDP 采集端口（Graylog）

- `variables.json`：

```json
{
  "access": [
    {
      "id": "http",
      "service": "graylog",
      "port": 9000,
      "public": true,
      "rootUrl": ["GRAYLOG_EXTERNAL_URL"],
      "endpoints": [
        {"roles": ["dashboard"], "scheme": "http"},
        {"roles": ["api"], "scheme": "http", "path": "/api/"}
      ]
    },
    {"id": "beats", "service": "graylog", "port": 5044, "public": true, "endpoints": []},
    {"id": "syslog-tcp", "service": "graylog", "port": 5140, "public": true, "endpoints": []},
    {"id": "syslog-udp", "service": "graylog", "port": 5140, "protocol": "udp", "public": true, "endpoints": []},
    {"id": "raw-tcp", "service": "graylog", "port": 5555, "public": true, "endpoints": []},
    {"id": "raw-udp", "service": "graylog", "port": 5555, "protocol": "udp", "public": true, "endpoints": []},
    {"id": "gelf-tcp", "service": "graylog", "port": 12201, "public": true, "endpoints": []},
    {"id": "gelf-udp", "service": "graylog", "port": 12201, "protocol": "udp", "public": true, "endpoints": []},
    {"id": "forwarder-data", "service": "graylog", "port": 13301, "public": true, "endpoints": []},
    {"id": "forwarder-config", "service": "graylog", "port": 13302, "public": true, "endpoints": []}
  ]
}
```

- `.env` 与 `docker-compose.yml` 配合：
  - `.env` 移除全部 `W9_*_PORT_SET`、`W9_HTTP_PORT`、`W9_URL`、`W9_URL_REPLACE`，定义 `GRAYLOG_EXTERNAL_URL=http://localhost:9001`。
  - `docker-compose.yml` 中设置 `GRAYLOG_HTTP_EXTERNAL_URI: "${GRAYLOG_EXTERNAL_URL}/"` 自动补齐 Graylog 要求的尾斜杠，`ports` 改为 `"9001:9000/tcp"`、`"5140:5140/tcp"`、`"5140:5140/udp"` 等固定默认映射。

### 8.4 多服务统一网关与路径后缀派生（Supabase）

- `variables.json`：

```json
{
  "access": [
    {
      "id": "gateway",
      "service": "api-gw",
      "port": 8000,
      "public": true,
      "rootUrl": ["SUPABASE_PUBLIC_URL"],
      "endpoints": [
        {"roles": ["dashboard", "gateway"], "scheme": "http"}
      ]
    }
  ]
}
```

- `.env` 与 `docker-compose.yml` 配合：
  - 内部 `studio`、`auth`、`rest`、`realtime`、`db` 等服务不直接对外暴露，不写入 `access`。
  - `SUPABASE_PUBLIC_URL` 接收网关主地址；需要后缀的认证地址通过原生配置拼接 `API_EXTERNAL_URL=${SUPABASE_PUBLIC_URL}/auth/v1`；面向用户外部前端的 `SITE_URL` 作为独立业务变量保留，不由网关域名覆盖。

### 8.5 多个独立 HTTP 端口与按需开放端口（Kong + RabbitMQ 模式）

```json
{
  "access": [
    {
      "id": "admin",
      "service": "kong",
      "port": 8002,
      "public": true,
      "endpoints": [{"roles": ["admin"], "scheme": "http"}]
    },
    {
      "id": "gateway",
      "service": "kong",
      "port": 8000,
      "public": true,
      "endpoints": [{"roles": ["gateway"], "scheme": "http"}]
    },
    {
      "id": "api",
      "service": "kong",
      "port": 8001,
      "public": true,
      "rootUrl": ["KONG_ADMIN_GUI_API_URL"],
      "endpoints": [{"roles": ["api"], "scheme": "http"}]
    },
    {
      "id": "status",
      "service": "kong",
      "port": 8100,
      "public": false,
      "endpoints": [{"roles": ["metrics"], "scheme": "http", "path": "/metrics"}]
    }
  ]
}
```

- 顺序即优先级：`admin`（Kong Manager，含 `ui` 角色）是**唯一被推荐**的默认域名端口组，其域名作为实例主域名；`gateway`（纯业务转发，`gateway` 角色）与 `api`（管理 API，`api` 角色）不含 `ui` 角色，默认不生成域名绑定，需要时可在高级区手动开启或安装后绑定。
- `admin`、`gateway`、`api` 三个 HTTP 端口组可分别独立控制端口开关、各自绑定不同域名；`api` 无论使用 IP:端口还是独立域名，其生效主地址均自动同步至 `KONG_ADMIN_GUI_API_URL`。上例中的 `status` 用于演示 `public: false` 按需开放端口模式（仓库当前实现未声明该端口组），仓库 Compose 默认不发布宿主机端口，用户可按需开启。

### 8.6 Web 主地址 + SSH 外部端口同步（GitLab）

- `variables.json`：

```json
{
  "access": [
    {
      "id": "http",
      "service": "gitlab",
      "port": 80,
      "public": true,
      "rootUrl": ["GITLAB_EXTERNAL_URL"],
      "endpoints": [
        {"roles": ["web", "api"], "scheme": "http"}
      ]
    },
    {
      "id": "ssh",
      "service": "gitlab",
      "port": 22,
      "public": true,
      "mappedPort": ["GITLAB_SSH_PORT"],
      "endpoints": [
        {"roles": ["ssh"], "scheme": "ssh"}
      ]
    }
  ]
}
```

- `.env` 与 `docker-compose.yml` 配合：
  - `.env` 移除 `W9_HTTP_PORT`、`W9_HTTP_PORT_SET`、`W9_SSH_PORT_SET`、`W9_URL`、`W9_URL_REPLACE`，保留原生配置变量 `GITLAB_EXTERNAL_URL=http://localhost:9001` 与 `GITLAB_SSH_PORT=9002`。
  - `docker-compose.yml` 端口映射写固定默认值 `'9001:80'` 与 `'9002:22'`（容器内部 SSH 监听固定在 `22`）；`GITLAB_OMNIBUS_CONFIG` 引用 `external_url '${GITLAB_EXTERNAL_URL}'` 与 `gitlab_rails['gitlab_shell_ssh_port'] = ${GITLAB_SSH_PORT}`。安装时修改外部 SSH 端口会自动同步至 `GITLAB_SSH_PORT`，保证界面展示的克隆端口准确一致。

### 8.7 强制域名与强制外部 HTTPS（Vaultwarden / Jitsi 模式）

- 容器内监听明文 HTTP，但浏览器端要求安全上下文且必须通过域名 HTTPS 访问（Vaultwarden）：

```json
{
  "access": [
    {
      "id": "http",
      "service": "vaultwarden",
      "port": 80,
      "public": false,
      "requireDomain": true,
      "requireHttps": true,
      "rootUrl": ["DOMAIN"],
      "endpoints": [
        {"roles": ["web", "api"], "scheme": "http"}
      ]
    }
  ]
}
```

- 容器内自身监听 HTTPS 且禁止裸 IP 访问（Jitsi / Teleport）：组内 `scheme: "https"` 已自动隐含强制外部 HTTPS，只需声明 `requireDomain: true`：

```json
{
  "access": [
    {
      "id": "https",
      "service": "web",
      "port": 8443,
      "public": false,
      "requireDomain": true,
      "rootUrl": ["PUBLIC_URL"],
      "endpoints": [
        {"roles": ["web"], "scheme": "https"}
      ]
    }
  ]
}
```

---

## 9. 消费端（Websoft9）同步改造建议

本库完成上述契约与应用包迁移后，消费端（`websoft9` 的 `apphub` 后端与 `console` 前端）建议按以下六个模块同步收敛：

### 9.1 应用商店契约升级与清单构建（`local_app_store.py`）

- **契约门控**：本库随 V2 `access[]` 全量落地已将 [metadata/appstore-schema.json](../metadata/appstore-schema.json) 中的 `library.schemaVersion` 升至 `"3"`。消费端实现下述改造后，再将商店同步模块支持的 `library` 契约版本加入 `"3"`；未升级旧版客户端会自动拒绝 `"3"` 并保留本地 `"2"` 快照。
- **现状**：依赖扫描 `.env` 中的 `W9_*_SET` 生成 `settings`，依赖 `"W9_URL" in env_values` 判断 `is_web_app`，依赖旧 `access.defaultScheme` 或 `W9_HTTPS_PORT` 推导 `default_scheme`，未向前端透传 `access`。
- **改造建议**：
  1. 解析仓库默认 `docker-compose.yml` 的 `ports`（及行尾 `# purpose` 注释），结合 `variables.json.access` 输出规范化的有序端口组模型（含 `id`、`service`、`port`、`protocol`、`public`、默认宿主机端口 `default_mapped_port`、`requireDomain`、`requireHttps`、能否绑定域名 `can_bind_domain`、`endpoints` 及可选的 `purpose` 说明）。
  2. `settings` 仅收集非端口类 `W9_*_SET` 业务输入项（如 API Key）；不再依赖 `W9_URL` 判断域名能力（只要任一端口组含 `http`/`https`/`ws`/`wss` 入口即具备域名反代能力）；并按候选端口组数量向安装表单透传可生成默认域名的端口组列表（首个为主域名，其余为附属域名）。

### 9.2 安装接口与部署编排（`schemas/appInstall.py`、`app_manager.py`、`runtime_install.py`）

- **现状**：`appInstall` 采用应用级单一 `proxy_enabled` + `domain_names` + `settings={"W9_HTTP_PORT_SET": ...}`，无法表达多端口开关与多服务独立域名；`runtime_install.py` 仍硬编码注入 `W9_HTTP_PORT_SET`、`W9_URL`、`W9_URL_REPLACE`。
- **改造建议**：
  1. 安装入参改为按端口组 `id` 提交实例访问配置：`ports: [{id, public, mapped_port, domains, primary_domain, certificate_id}]`（对单 HTTP 端口组应用可保持向后兼容简写）。
  2. 安装前置校验执行第 6 节约束：`requireDomain: true` 必须提供 `domains`；含 `rootUrl` / `host` 的端口组必须至少满足 `public: true` 或提供 `domains`；启用宿主机映射的端口执行宿主机端口占用检测。
  3. 生成实例 Compose 时，按实例端口配置**整组替换**受管服务的 `ports`（如使用 `!override` 或直接渲染最终编排），确保 `public: false` 真正移除对应宿主机监听；保留 `x-websoft9-unmanaged-ports` 明确豁免的映射，并将它们计入端口占用检测。
  4. 启动前按端口组计算生效主地址与映射端口，精确按键名写入 `rootUrl`、`host`、`mappedPort` 所列 `.env` 变量；`runtime_install.py` 改为写入运行时模板声明的原生端口与地址变量。

### 9.3 实例访问概览与网关反代管理（`app_access_manager.py`）

- **现状**：`AppAccessProfile` 仅支持单应用单一目标（靠 `W9_HTTP_PORT` / `W9_HTTPS_PORT` 定位容器名为 `app_id` 的主容器），网关配置只读单一 `src/nginx-proxy.conf`。
- **改造建议**：
  1. 实例持久化保存各端口组的绑定记录（关联端口组 `id`、`proxy_id`、`domains`、`primary_domain`）。
  2. 反代上游目标通过 Compose 标签（`com.docker.compose.project` + `com.docker.compose.service == group.service`）在同一应用共享网络内精准定位容器与容器内部 `group.port`，彻底摆脱对 `W9_HTTP_PORT` 和固定主容器名的依赖；上游转发协议按组内入口协议映射（`https`/`wss` 走 `https`，`http`/`ws` 走 `http`，并保持 WebSocket Upgrade 开启）。
  3. 当组内存在 `scheme` 为 `"https"` / `"wss"` 或 `group.requireHttps == true` 时，创建/更新 Proxy Host 强制挂载证书（未传 `certificate_id` 时自动申请或使用内置证书 `ensure_inner_certificate`）并锁定 `ssl_forced=True`。
  4. 注入高级 Nginx 配置时优先读取 `src/nginx-proxy-<group.id>.conf`，不存在时回退读取单端口通用的 `src/nginx-proxy.conf`。

### 9.4 多域名与主地址更新（替代旧 `_update_gitea_env_file`）

- **现状**：`_update_gitea_env_file` 使用 `env_file_content.replace(old_url, new_url)` 全文字符串替换，易误伤其他变量，且无法处理 `http` ↔ `https` 协议切换。
- **改造建议**：
  1. 废弃全文 `.replace()`，改为解析 `.env` 行结构按变量名精确赋值（保留原有注释与未改动行）。
  2. 端口组未声明 `rootUrl` / `host` 时，增删改域名仅调用网关 API，不改 `.env`、不触发 `redeploy_app`。
  3. 端口组声明了 `rootUrl` / `host` 时：增删非主域名仅改网关；切换主域名、主域名证书状态变更（影响 `http`/`https`）或删除主域名触发回退时，先校验目标变量不在 `env.first_startup_only` 锁定范围内，再精确更新 `.env` 并触发 `redeploy_app`。

### 9.5 前端安装弹窗、端口展示与中英文国际化（`console`）

- **安装时显示哪些端口与默认值**：
  1. `access: []`（如纯命令行工具）：隐藏端口与域名配置区块。
  2. `access` 非空时：按 `access[]` 数组顺序驱动端口列表。单端口组应用直接展示主端口开关（初始值为 `group.public`）与宿主机端口输入框（初始值为 `default_mapped_port`，若宿主机端口冲突可自动推荐空闲端口）；多端口组应用在首屏展示首个主端口组，其余端口组（如 `ssh`、日志采集端口）收纳在“端口与高级设置”中按序展开。
  3. 域名区域只为**推荐集合**渲染默认启用行，其余可绑域名端口组收纳在「端口与域名（高级）」内默认关闭：推荐集合中的第一行是主域名，预填 `{app}.{根域名}`，其生效地址写入该组 `rootUrl`；其余推荐行预填派生建议 `{app}-{group.id}.{根域名}`（`group.id` 中的 `_` 规范化为 `-`）；非推荐的组由用户在高级区打开后才预填同样规则并创建绑定；`requireDomain: true` 的行无论是否推荐都强制启用且必填、不可关闭；`requireHttps: true` 或组内 `scheme` 为 `https`/`wss` 的行提示强制 HTTPS。
- **哪些端口组默认推荐绑定域名（推荐集合）**：
  1. **主规则**：端口组内任一端口的 `roles` 含 `kind == ui` 的角色（`web`、`admin`、`dashboard`、`notebook`、`remote-desktop`）→ 推荐。用户会用浏览器直接打开这些入口，不绑域名就只能靠 `IP:端口` 访问。
  2. **回退规则**：应用**完全没有** `ui` 类角色（如 `vespa`、`weaviate`、`milvus` 等无浏览器界面的服务）→ 仅取首个域名候选组推荐，保证装完至少有一个可解析入口；其余组不推荐。
  3. **不推荐**：纯 `gateway`（如 Kong `8000`、Traefik `80`）、`metrics`（如 Milvus `metrics`、Kong `status`）、以及仅作内部管理/监控用的 `api` 端口组。原因：这些入口要么承载用户自有业务域名（平台快捷域名占用会与业务域名冲突），要么由程序调用而非浏览器访问，默认绑域名只增加证书与 DNS 负担。
  4. **强制例外**：`requireDomain: true` 的组不受上述筛选约束，永远默认启用且必填。
- **“默认域名”的数量语义**：
  1. **默认域名数量 = 推荐集合大小，可以为 0、1 或多个**：纯 TCP/UDP 或无任何 HTTP 入口的应用（如 `redis`、`rabbitmq` 的 `amqp`）为 0，不渲染域名区域；`kong`、`opensearch`、`traefik` 等为 1；`librechat`（`web` + `admin`）、`selenium`（`grid` + `novnc`）、`tensorflow`（`notebook` + `tensorboard`）为 2。
  2. **主域名：唯一**。推荐集合中的第一行为主域名（其地址写入该组 `rootUrl`），其余为附属域名；切换主域名不影响其他端口组已绑定的域名。
  3. **必须绑定域名：可以多个**。契约未限制 `requireDomain: true` 的端口组数量；**每个**声明该字段的端口组都必须各自提供域名才能提交安装，且该行不可关闭。
  4. **同一实例内域名唯一**，跨行不得重复；主域名被修改后，仍保持自动派生值（未被手动编辑过）的行按同一规则重算，已被手动编辑的行保持不变。
  5. 未推荐但被用户手动开启的组，与推荐组行为一致：可绑定多域名、可按 `rootUrl` / `host` 决定是否同步 `.env`；关闭后回退为 `http(s)://<host>:<published_port>`（要求其 `public: true`）。
- **端口名称中英文显示机制（无需依赖 `i18n/translation.json` 或在 `variables.json` 塞入双语文案）**：
  `console` 前端复用并升级内置 `resources.ts` 国际化字典，按以下三级规则确定性渲染端口标签，并统一附带 `(<port>/<TCP|UDP>)` 技术标识消歧：
  1. **标准端口组 `id` / 首选入口 `role` 精确映射**：如 `web`/`http` → `HTTP 访问端口` / `HTTP Port`，`https` → `HTTPS 访问端口` / `HTTPS Port`，`admin` → `管理后台端口` / `Admin Port`，`dashboard`/`studio` → `控制台端口` / `Dashboard Port`，`api` → `API 端口` / `API Port`，`db` → `数据库端口` / `Database Port`，`ssh` → `SSH 端口` / `SSH Port`，`gateway` → `网关端口` / `Gateway Port`，`grpc` → `gRPC 端口` / `gRPC Port`，`metrics` → `监控指标端口` / `Metrics Port`，`notebook` → `Notebook 端口` / `Notebook Port`，`novnc`/`remote-desktop` → `远程桌面端口` / `Remote Desktop Port`。
  2. **复合/专有 `group.id` 按 `-` 分词走 `settingTokens` 词根组合翻译**：如 `syslog-udp` → `Syslog UDP 端口` / `Syslog UDP Port`，`forwarder-config` → `转发器配置端口` / `Forwarder Config Port`，`calls-udp` → `通话 UDP 端口` / `Calls UDP Port`。
  3. **回退与辅助说明**：未命中词根时将 `group.id` 首字母大写化并拼接 `(<port>/<protocol>)`，同时可将 `docker-compose.yml` 端口行强制携带的 `# purpose` 注释作为辅助副标题或 Tooltip 展示。
- **我的应用 -> 访问面板**：按 `ui → api → infra` 分组渲染全部有效入口地址（宿主直连取 Docker 实时 `PortBindings`，域名地址取对应端口组绑定的域名 + `endpoint.path` + `query`）；每个可绑域名端口组独立管理其多域名列表，仅在声明了 `rootUrl` / `host`（且非首次启动只读锁定）的端口组上展示“设为主域名”按钮。初始化凭据与命令继续复用现有 `credentials`、`cli_commands` 与 `help.login` 面板。

### 9.6 存量已安装实例兼容过渡

- 消费端升级后，老实例仓库若仍为旧版（无 V2 `access` 数组、`.env` 仍含 `W9_URL` / `W9_*_PORT_SET`），访问管理模块可保留一层只读兼容分支按旧 `.env` 解析，**不强制改写运行中老实例的编排文件**；新安装实例全部走新版 `access` 契约。