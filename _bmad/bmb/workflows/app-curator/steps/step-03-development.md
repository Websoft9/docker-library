# 阶段 3：开发与生成（Development）

## 目标

**基于阶段 2 批准的计划文档，生成完整的应用文件。**

核心任务：
1. **执行已确认的决策** — 所有 W9_* 决策已在阶段 2 确认，此阶段只执行不重新决策
2. **按清单生成文件** — 严格按照阶段 2 Phase 7b 的文件清单逐一生成
3. **完整性验证** — 确保所有文件相互引用正确、语法有效

## 执行原则

- 🔧 **执行不决策**：W9_LOGIN_*、W9_URL_REPLACE 等已在阶段 2 确认，直接使用 `confirmed_decisions`
- 📋 **忠实计划**：按 `app-plan.md` 中的预览内容生成文件，不擅自修改
- 📦 **真实模式**：参考真实应用格式（wordpress、gitlab、nginx），不使用虚构字段
- ✅ **边生成边验证**：每生成一个文件立即检查，发现问题立即修正

---

## 前置条件

✅ 阶段 2 分析完成（state.json 中 `analysis.completed = true`）
✅ 用户已批准计划文档（`user_decision = "approved"`）
✅ 计划文档 `_bmad-output/workflows/{app_name}/app-plan.md` 存在
✅ `confirmed_decisions` 数据已保存在 state.json

---

## 开发流程

### 流程概览

```
Phase 1  → 加载计划数据与准备
Phase 2  → 创建目录结构
Phase 3  → 生成 .env 文件
Phase 4  → 生成 docker-compose.yml
Phase 5  → 创建 src/ 配置文件
Phase 6  → 生成 variables.json
Phase 7  → 生成 CHANGELOG.md + Notes.md
Phase 8  → 文件完整性验证
Phase 9  → 开发报告与阶段切换
```

---

### Phase 1: 加载计划数据与准备

**操作：** 读取 state.json 和 app-plan.md，提取所有开发所需数据

#### Step 1a: 加载 state.json

```
读取: _bmad-output/workflows/{app_name}/state.json

提取关键数据:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app_name:          {从 state.json}
issue_url:         {从 research_data}

confirmed_decisions:
  w9_login_user:   { required: true/false, value: "admin/root/...", confirmed: true }
  w9_url_replace:  { required: true/false, confirmed: true }

research_data:
  basic_info:      { image, version, image_source }
  architecture:    { service_count, services[], ports[] }
  official_compose: { raw_content, source_url }
```

#### Step 1b: 加载计划文档

```
读取: _bmad-output/workflows/{app_name}/app-plan.md

提取已批准的内容:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  .env 预览        → Phase 3 直接使用
  compose 预览      → Phase 4 直接使用
  src/ 文件清单     → Phase 5 直接使用
  改造说明         → Notes.md 引用
  测试策略         → 传递给 step-04
  文件清单         → Phase 2-7 按序执行
```

#### Step 1c: 准备检查

```
✅ 数据完整性:
  [✅/❌] state.json 可读且 analysis.completed = true
  [✅/❌] app-plan.md 存在且非空
  [✅/❌] confirmed_decisions 中所有决策 confirmed = true
  [✅/❌] compose 预览内容有效

⚠️ 如果任何检查失败 → 停止，提示返回阶段 2 修正
```

---

### Phase 2: 创建目录结构与清理模板残留

**操作：** 创建应用目录、src/ 子目录，并清理模板 shell 残留文件

```bash
mkdir -p apps/{app_name}/src
```

#### Step 2b: 清理模板残留文件

⚠️ **关键：** 如果应用目录已从模板 shell 创建，可能包含与当前应用无关的残留文件。必须在生成新文件前清理。

**必须检查并删除的模板残留：**

| 文件 | 条件 | 说明 |
|------|------|------|
| `Dockerfile` | 不使用自定义构建 | 模板 shell 可能包含其他应用的 Dockerfile |
| `README.jinja2` | 始终删除 | 已被 `template/README.jinja2` 全局模板取代 |

```bash
cd apps/{app_name}
[ -f Dockerfile ] && rm -f Dockerfile
[ -f README.jinja2 ] && rm -f README.jinja2
```

> ⚠️ **src/ 残留文件清理推迟到 Phase 5e（生成 src/ 文件后执行）。**
> 原因：此时 docker-compose.yml 尚未生成（Phase 4），无法对照 volumes 映射判断哪些 src/ 文件应保留。

**验证：**
```
✅ apps/{app_name}/     目录已创建
✅ apps/{app_name}/src/ 子目录已创建
✅ Dockerfile、README.jinja2 等已清理
```

---

### Phase 3: 生成 .env 文件

**操作：** 基于阶段 2 Step 3e 的完整 .env 预览生成文件

#### Step 3a: .env 文件结构

⚠️ **核心原则：只包含当前应用需要的变量，不写冗余行。每个变量都必须有存在的理由。**

> **参考源文件：** `template/.env` 是所有 W9_* 变量的权威定义。新增任何 W9_ 变量前先对照该模板。

**变量分类说明：**

.env 中的变量分两类，agent 必须理解此区分：

| 类型 | 说明 | 在 compose 中引用? | 示例 |
|------|------|:-:|------|
| **容器运行时变量** | 被 docker-compose.yml 引用，影响容器行为 | ✅ | `W9_REPO`, `W9_VERSION`, `W9_ID`, `W9_POWER_PASSWORD`, `W9_HTTP_PORT_SET`, `W9_NETWORK`, `W9_URL`, `W9_RCODE` |
| **平台元数据变量** | 仅存在于 .env，由 Websoft9 部署平台消费，容器运行时不感知 | ❌ | `W9_DIST`, `W9_DB_EXPOSE`, `W9_KEY_SET`, `W9_URL_REPLACE`, `W9_ADMIN_PATH`, `W9_DB_VERSION`, `W9_URL_WITH_PORT`, `W9_NAME` |

**完整 W9_* 变量参考表（362 个应用统计）：**

| 变量 | 使用率 | 类型 | 位置 | 说明 |
|------|--------|------|------|------|
| `W9_REPO` | 333/362 | 运行时 | Image | Docker 镜像名 |
| `W9_DIST` | 330/362 | 元数据 | Image | 发行版标识，几乎全部为 `community` |
| `W9_VERSION` | 357/362 | 运行时 | Image | 镜像版本标签 |
| `W9_POWER_PASSWORD` | 236/362 | 运行时 | Auth | 统一主密码，所有服务密码引用它 |
| `W9_HTTP_PORT_SET` | 306/362 | 运行时 | Ports | 宿主机 HTTP 映射端口 |
| `W9_HTTPS_PORT_SET` | 47/362 | 运行时 | Ports | 宿主机 HTTPS 映射端口 |
| `W9_DB_PORT_SET` | 49/362 | 运行时 | Ports | 宿主机数据库端口 |
| `W9_SSH_PORT_SET` | 39/362 | 运行时 | Ports | 宿主机 SSH 端口（gitea/gitlab/gogs） |
| `W9_KEY_SET` | 34/362 | 元数据 | Ports | Secret key 占位符，由平台管理 |
| `W9_ID` | 336/362 | 运行时 | System | 实例标识（容器命名前缀） |
| `W9_HTTP_PORT` | 319/362 | 运行时 | System | 容器内部 HTTP 端口 |
| `W9_HTTPS_PORT` | 46/362 | 运行时 | System | 容器内部 HTTPS 端口 |
| `W9_LOGIN_USER` | 144/362 | 元数据 | System | 管理员用户名 |
| `W9_LOGIN_PASSWORD` | 149/362 | 运行时 | System | 管理员密码（引用 $W9_POWER_PASSWORD） |
| `W9_ADMIN_PATH` | 61/362 | 元数据 | System | 管理后台 URL 路径 |
| `W9_DB_EXPOSE` | 144/362 | 元数据 | System | 声明数据库类型（mysql/postgresql/mariadb/mongodb/redis） |
| `W9_DB_VERSION` | 40/362 | 元数据 | System | compose 自包含数据库的版本号 |
| `W9_URL` | 320/362 | 运行时 | System | 外部 URL 占位符 |
| `W9_URL_REPLACE` | 121/362 | 元数据 | System | 是否在首次启动时替换 W9_URL |
| `W9_URL_WITH_PORT` | 6/362 | 元数据 | System | `false` 时 URL 不含端口 |
| `W9_NETWORK` | 359/362 | 运行时 | System | Docker 网络名，恒为 `websoft9` |
| `W9_RCODE` | 22/362 | 运行时 | App | 内部随机密码（独立于 W9_POWER_PASSWORD）|
| `W9_NAME` | 21/362 | 元数据 | App | 应用显示名称（少数应用需要） |

> `W9_LOGIN_*` 扩展变体: 少数应用使用 `W9_LOGIN_API_KEY`, `W9_LOGIN_JWT_SECRET`, `W9_LOGIN_TOKEN` 等。

**端口变量命名规范 `W9_{FUNCTION}_PORT_SET`（重要）：**

每个需要暴露到宿主机的端口都必须有一对变量：
- `W9_{FUNCTION}_PORT_SET` — 宿主机映射端口（用户可修改），位于 **分隔线上方**
- `W9_{FUNCTION}_PORT` — 容器内部监听端口（固定值），位于 **分隔线下方**

**标准端口变量（4 个，覆盖大部分场景）：**

| 变量 | 使用率 | 用途 | 默认端口 |
|------|--------|------|----------|
| `W9_HTTP_PORT_SET` / `W9_HTTP_PORT` | 306/362 | Web HTTP 访问 | 9001 / 80 or 8080 |
| `W9_HTTPS_PORT_SET` / `W9_HTTPS_PORT` | 47/362 | Web HTTPS 访问 | 9443 / 443 |
| `W9_DB_PORT_SET` / `W9_DB_PORT` | 49/362 | 数据库端口 | 取决于 DB 类型 |
| `W9_SSH_PORT_SET` / `W9_SSH_PORT` | 39/362 | SSH/Git 端口 | 2222 / 22 |

**自定义端口变量（25 个应用使用，39 种变量名）：**

当应用需要暴露 **标准 4 个之外** 的端口时，按 `W9_{协议或功能}_PORT_SET` 命名。

| 功能分类 | 变量名示例 | 应用示例 |
|----------|-----------|----------|
| API 端口 | `W9_API_PORT_SET` | minio, killbill, saleor, opencost |
| 消息队列 | `W9_MQTT_PORT_SET`, `W9_AMQP_PORT_SET`, `W9_MQ_PORT_SET`, `W9_BROKER_PORT_SET` | emqx, mosquitto, activemq, rabbitmq, rocketmq |
| 管理界面 | `W9_DASHBOARD_PORT_SET`, `W9_GUI_PORT_SET`, `W9_ADMIN_GUI_PORT_SET`, `W9_ADMIN_API_PORT_SET` | adguardhome, opensearch, tensorflow, kong |
| 协议专用 | `W9_STOMP_PORT_SET`, `W9_OPENWIRE_PORT_SET`, `W9_RPC_PORT_SET` | activemq, aria2 |
| 流媒体 | `W9_RTMP_PORT_SET`, `W9_FLV_PORT_SET` | srs |
| 网络/DNS | `W9_DNS_TCP_PORT_SET`, `W9_DNS_UDP_PORT_SET` | adguardhome, consul |
| 日志采集 | `W9_BEATS_TCP_PORT_SET`, `W9_SYSLOG_TCP_PORT_SET`, `W9_GELF_UDP_PORT_SET` 等 | graylog (9 个端口) |
| 邮件 | `W9_SMTP_PORT_SET` | mailpit |
| 通用传输 | `W9_TCP_PORT_SET`, `W9_UDP_PORT_SET`, `W9_WS_PORT_SET` | tinyproxy, palworld, mosquitto |
| 连接管理 | `W9_CLIENT_PORT_SET`, `W9_SERVER_PORT_SET`, `W9_TURN_PORT_SET`, `W9_REMOTE_PORT_SET` | zookeeper, frp, screego, srs |

**决策规则 — 何时需要自定义端口变量：**

```
判断流程:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 应用只有一个 HTTP Web 端口?
   → 只需 W9_HTTP_PORT_SET（覆盖 80% 的应用）

2. 应用还提供 HTTPS、数据库、SSH 端口?
   → 加上 W9_HTTPS_PORT_SET / W9_DB_PORT_SET / W9_SSH_PORT_SET

3. 应用有标准 4 个之外的额外端口需要暴露给用户?
   → 创建 W9_{功能名}_PORT_SET，命名规则:
     ✅ 用协议名: MQTT, AMQP, RTMP, SMTP, DNS
     ✅ 用功能名: API, DASHBOARD, ADMIN_GUI, RPC
     ✅ 全大写，下划线分隔
     ❌ 不要用通用名如 W9_PORT2_PORT_SET

4. 应用有多个同类端口（如 TCP + UDP）?
   → 用 W9_{功能}_{协议}_PORT_SET，如:
     W9_DNS_TCP_PORT_SET / W9_DNS_UDP_PORT_SET
     W9_SYSLOG_TCP_PORT_SET / W9_SYSLOG_UDP_PORT_SET

5. 中间件无 HTTP 入口但有核心协议端口?
   → 用 W9_DB_{中间件}_PORT_SET（如 kafka）或 W9_{协议}_PORT_SET
     示例: W9_DB_KAFKA_PORT_SET='9092', W9_CLIENT_PORT_SET='2181'
```

**compose 中的端口引用方式：**
```yaml
ports:
  - $W9_HTTP_PORT_SET:$W9_HTTP_PORT      # 标准 HTTP
  - $W9_MQTT_PORT_SET:1883               # 自定义端口（内部端口可直接写数字）
  - "$W9_DNS_UDP_PORT_SET:53/udp"         # UDP 端口需要 /udp 后缀
```

**标准模板（结构化注释版，按需裁剪）：**

```env
# {Application Name} on Docker - Environment Configuration
# Edit this file to customize the deployment settings.
# Full documentation: {official_docs_url}

# =========================================================
# Image
# version tags refer to: {dockerhub_tags_url}
# =========================================================
W9_REPO={image_name}
W9_DIST='community'
W9_VERSION='{version}'

{如果有内置认证、数据库或需要密码的服务}
# =========================================================
# Authentication
# Initial administrator credentials for first login
# =========================================================
W9_POWER_PASSWORD='{auto_generated_16char}'
{end}

# =========================================================
# Ports & User Settings
# W9_xxx_xxx_SET — user can modify when creating app
# Each SET port has a matching internal port (W9_xxx_PORT) below the separator
# =========================================================
W9_HTTP_PORT_SET='9001'
# W9_HTTPS_PORT_SET='9443'   # Uncomment if app supports HTTPS
# W9_DB_PORT_SET='3306'      # Uncomment to expose database port (mysql=3306, pg=5432)
# W9_SSH_PORT_SET='2222'     # Uncomment if app has SSH access (e.g. Gitea, GitLab)
{如果应用有额外协议/功能端口需要暴露}
W9_{FUNCTION}_PORT_SET='{port}'    # {功能说明}，如 W9_MQTT_PORT_SET='1883'
{end}
{如果应用需要 secret key}
W9_KEY_SET='dfsjdkjf77xjxcjcj'    # Secret key placeholder, replaced by platform
{end}

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

# =========================================================
# System (managed by Websoft9, do not modify)
# =========================================================
W9_ID='{app_name}'
W9_HTTP_PORT={internal_http_port}
{如果应用有 HTTPS 内部端口}
W9_HTTPS_PORT={internal_https_port}
{end}
{如果 confirmed_decisions.w9_login_user.required = true}
W9_LOGIN_USER={admin_username}
W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD
{end}
{如果有 admin path}
W9_ADMIN_PATH="/{admin_path}"
{end}
{如果有数据库服务}
W9_DB_EXPOSE="{mysql|postgresql|mariadb|mongodb|redis}"
W9_DB_VERSION="{db_version}"
{end}
W9_URL='internet_ip:$W9_HTTP_PORT_SET'
{如果 confirmed_decisions.w9_url_replace.required = true}
W9_URL_REPLACE=true
{end}
{如果应用 URL 不含端口}
W9_URL_WITH_PORT=false
{end}
W9_NETWORK=websoft9

{如果有应用特定环境变量}
#### --------------------------------------------------------------------------------------- ####

# =========================================================
# Application-specific settings
# Official environment variable reference: {official_env_docs_url}
# =========================================================
{app_specific_env_var_1}={value}
{app_specific_env_var_2}={value}
# {OPTIONAL_VAR}={example_value}   # Uncomment to enable: {explanation}
{如果应用需要独立于 W9_POWER_PASSWORD 的内部随机密码}
W9_RCODE='{auto_generated_14char}'    # Internal random password for DB/services
{end}
{如果应用需要显示名称}
W9_NAME='{display_name}'
{end}
{end}
```

**条件裁剪规则：**

| 变量/节 | 何时包含 | 何时省略 |
|---------|----------|----------|
| **文件头注释块** | 始终 | — |
| **Image 节** (`W9_REPO`, `W9_DIST`, `W9_VERSION`) | 始终 | — |
| **Auth 节** + `W9_POWER_PASSWORD` | 有内置认证、数据库或任何需要密码的服务 | 无认证且无数据库（如 nginx、drawio） |
| **Ports 节** | 始终 | — |
| `W9_HTTPS_PORT_SET` (注释) | 始终保留（注释形式），已知支持 HTTPS 则取消注释 | — |
| `W9_DB_PORT_SET` (注释) | 有数据库服务时保留（注释形式） | 无数据库 |
| `W9_SSH_PORT_SET` (注释) | 有 SSH/Git 端口时保留 | 无 SSH 功能 |
| `W9_{FUNCTION}_PORT_SET` | 应用暴露标准 4 端口之外的协议/功能端口（参照端口命名规范） | 无额外端口 |
| `W9_KEY_SET` | 应用需要 API key / secret key 由平台注入 | 无密钥需求 |
| `W9_ID` | 始终 | — |
| `W9_HTTP_PORT` | 始终 | — |
| `W9_HTTPS_PORT` | 容器内部有 HTTPS 监听 | 无 HTTPS |
| `W9_LOGIN_USER`/`PASSWORD` | 有内置管理员认证（环境变量可预配置） | 无认证、setup wizard、仅 token |
| `W9_ADMIN_PATH` | 有独立管理后台路径（如 `/wp-admin`） | 无单独管理入口 |
| `W9_DB_EXPOSE` | compose 包含数据库服务 | 无数据库 |
| `W9_DB_VERSION` | compose 包含数据库服务且版本绑定 | 无数据库 |
| `W9_URL` | 始终 | — |
| `W9_URL_REPLACE` | `W9_URL` 在 compose environment 中被引用 | compose 未引用 W9_URL |
| `W9_URL_WITH_PORT` | 应用 URL 不应包含端口号（如域名模式） | 默认（URL 含端口） |
| `W9_NETWORK` | 始终 | — |
| **App-specific 节** | 有应用特定配置变量 | 无应用特定变量 |
| `W9_RCODE` | 需要独立于 `W9_POWER_PASSWORD` 的内部随机密码 | 所有密码统一用 `W9_POWER_PASSWORD` |
| `W9_NAME` | 应用需要显示名称变量 | 大多数应用不需要 |

#### Step 3b: 关键生成规则

```
规则 1: W9_REPO 格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ Docker Official Image: W9_REPO=wordpress (无前缀)
  ⚠️ Verified Publisher:    W9_REPO=gitlab/gitlab-ce (org/repo)
  📦 Community:             W9_REPO=author/image (author/repo)

规则 2: W9_VERSION 格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 使用具体版本号，不使用 latest
  ✅ 用单引号包裹: W9_VERSION='6.9'
  ✅ 版本号来自 research_data.basic_info.version

规则 3: W9_POWER_PASSWORD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 生成 16 位随机密码（含大小写字母 + 数字 + 特殊字符）
  ✅ 用单引号包裹
  ✅ 所有数据库密码引用 $W9_POWER_PASSWORD
  ✅ 无认证无数据库的纯静态应用(nginx, drawio)不需要此变量
  ⚠️ W9_RCODE: 当应用需要独立于主密码的内部随机密码时使用
     例: discourse 的 PostgreSQL 密码用 $W9_RCODE 而非 $W9_POWER_PASSWORD
     生成规则同 W9_POWER_PASSWORD（14 位随机）

规则 4: 分隔线格式
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 分隔线上方: 用户可修改的变量（镜像版本、密码、端口、KEY_SET）
  ✅ 分隔线下方: 系统变量 + 平台元数据变量（重建时不可修改）
  ✅ 第二条分隔线下方: 应用特定变量 + W9_RCODE + W9_NAME
  ✅ 使用精确的分隔注释格式:
     #### --  Not allowed to edit below ...  -- ####
     #### ---------------------------------------- ####  (第二条，如有应用变量区)

规则 4b: 平台元数据变量（关键概念）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ⚠️ 以下变量仅存在于 .env，从不在 docker-compose.yml 中引用
  ⚠️ 它们由 Websoft9 部署平台消费，不影响容器运行
  ✅ W9_DIST          — 发行版标识 (community/enterprise)
  ✅ W9_DB_EXPOSE     — 声明此应用使用的数据库类型
  ✅ W9_DB_VERSION    — 声明数据库镜像版本
  ✅ W9_KEY_SET       — Secret key 占位符，平台注入实际值
  ✅ W9_URL_REPLACE   — 通知平台在首次启动时替换 W9_URL
  ✅ W9_ADMIN_PATH    — 通知平台管理后台 URL 路径
  ✅ W9_URL_WITH_PORT — 通知平台 URL 是否不含端口
  ✅ W9_NAME          — 应用显示名称
  ✅ W9_LOGIN_USER    — 通知平台管理员用户名（展示给用户）

规则 5: 注释规范
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 文件首行: # {App Name} on Docker - Environment Configuration（结构化注释块）
  ✅ Image 区块内: # version tags refer to: {dockerhub_tags_url}
  ✅ 可选变量注释掉示例: # W9_HTTPS_PORT_SET='9443'
  ✅ 应用变量区首行: # Official environment variable reference: {docs_url}
  ✅ 行内注释说明特殊变量用途（紧跟变量后）
  ✅ 可选的应用变量注释形式保留: # SOME_VAR=value   # Uncomment to enable: ...
  ❌ 不写无意义注释（如 # This is the ID）
  📝 注意: 旧应用可能使用简洁格式（首行直接是 # version tags refer to:），新创建的应用统一使用结构化注释格式

规则 6: 引号风格
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 所有字符串值用单引号: W9_VERSION='3.4'
  ✅ 包含 $ 引用的值不用引号: W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD
  ✅ 包含 ${} 的复合值用双引号: NEXTCLOUD_TRUSTED_DOMAINS="\*"
  ❌ 不要混用单双引号

规则 7: 应用特定变量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✅ 数据库主机: {APP}_DB_HOST=$W9_ID-{db_name}
  ✅ 数据库密码: {APP}_DB_PASSWORD=$W9_POWER_PASSWORD
  ✅ 数据库名称: {APP}_DB_NAME=$W9_ID
  ✅ 数据库用户: {APP}_DB_USER=$W9_ID
  ✅ 保留官方变量名（如 WORDPRESS_DB_HOST 不改为 DB_HOST）
```

#### Step 3c: 真实应用参考

**📌 场景 A：有认证 + 有 URL 替换（WordPress 模式）**

```env
# WordPress on Docker - Environment Configuration
# Edit this file to customize the deployment settings.
# Full documentation: https://hub.docker.com/_/wordpress

# =========================================================
# Image
# version tags refer to: https://hub.docker.com/_/wordpress
# =========================================================
W9_REPO=wordpress
W9_DIST='community'
W9_VERSION='6.9'

# =========================================================
# Authentication
# Initial administrator credentials for first login
# =========================================================
W9_POWER_PASSWORD='NYvg!hilh9Haouf2'

# =========================================================
# Ports
# =========================================================
W9_HTTP_PORT_SET='9001'
# W9_HTTPS_PORT_SET='9443'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

# =========================================================
# System (managed by Websoft9, do not modify)
# =========================================================
W9_ID='wordpress'
W9_HTTP_PORT=80
W9_LOGIN_USER=admin
W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD
W9_ADMIN_PATH="/wp-admin"
W9_DB_EXPOSE="mysql"
W9_DB_VERSION="8.0"
#wordpress have write w9_url to database, You can set W9_URL using  your true URL or ""
W9_URL=''
W9_URL_REPLACE=true
W9_NETWORK=websoft9
#### --------------------------------------------------------------------------------------- ####

# =========================================================
# Application-specific settings
# Official environment variable reference: https://hub.docker.com/_/wordpress
# =========================================================
WORDPRESS_DB_HOST=$W9_ID-mysql
WORDPRESS_DB_USER=$W9_ID
WORDPRESS_DB_PASSWORD=$W9_POWER_PASSWORD
WORDPRESS_DB_NAME=$W9_ID
WORDPRESS_ROOT_URL="http://$W9_URL"
# WORDPRESS_DEBUG=1    # Uncomment to enable WP_DEBUG
```

**📌 场景 B：有认证 + 无 URL 替换（Grafana 模式）**

```env
# Grafana on Docker - Environment Configuration
# Edit this file to customize the deployment settings.
# Full documentation: https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/

# =========================================================
# Image
# version tags refer to: https://hub.docker.com/r/grafana/grafana/tags
# =========================================================
W9_REPO=grafana/grafana-oss
W9_DIST='community'
W9_VERSION='12.1.1'

# =========================================================
# Authentication
# Initial administrator credentials for first login
# =========================================================
W9_POWER_PASSWORD='5PidNEsE5!D314t0'

# =========================================================
# Ports
# =========================================================
W9_HTTP_PORT_SET='9001'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

# =========================================================
# System (managed by Websoft9, do not modify)
# =========================================================
W9_ID='grafana'
W9_HTTP_PORT=3000
W9_LOGIN_USER=admin
W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD
W9_URL='internet_ip:$W9_HTTP_PORT_SET'
W9_NETWORK=websoft9
#### --------------------------------------------------------------------------------------- ####

# =========================================================
# Application-specific settings
# env format: GF_<SectionName>_<KeyName> — refer to grafana.ini
# https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#variable-expansion
# =========================================================
GF_SECURITY_ADMIN_USER=${W9_LOGIN_USER}
GF_SECURITY_ADMIN_PASSWORD=${W9_POWER_PASSWORD}
GF_LOG_MODE=console file
# GF_DATABASE_URL=mysql://user:pass@host:3306/grafana   # Uncomment to use MySQL backend
```

**📌 场景 C：无认证 + 无数据库（nginx / debezium 模式）**

```env
# NGINX on Docker - Environment Configuration
# Edit this file to customize the deployment settings.
# Full documentation: https://hub.docker.com/_/nginx

# =========================================================
# Image
# version tags refer to: https://hub.docker.com/_/nginx/tags
# =========================================================
W9_REPO=nginx
W9_DIST='community'
W9_VERSION='1.29'

# =========================================================
# Ports
# =========================================================
W9_HTTP_PORT_SET='9001'
# W9_HTTPS_PORT_SET='9443'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

# =========================================================
# System (managed by Websoft9, do not modify)
# =========================================================
W9_ID='nginx'
W9_HTTP_PORT=80
W9_URL='internet_ip:$W9_HTTP_PORT_SET'
W9_NETWORK=websoft9
```

**📌 场景 D：中间件 / 无 HTTP（Kafka 模式）**

```env
# Kafka on Docker - Environment Configuration
# Edit this file to customize the deployment settings.
# Full documentation: https://github.com/bitnami/containers/tree/main/bitnami/kafka

# =========================================================
# Image
# version tags refer to: https://hub.docker.com/r/bitnami/kafka/tags
# =========================================================
W9_REPO=bitnami/kafka
W9_DIST='community'
W9_VERSION='4.0'

# =========================================================
# Authentication
# =========================================================
W9_POWER_PASSWORD='5xd!n4MoJl8OBI2f'

# =========================================================
# Ports
# =========================================================
W9_DB_KAFKA_PORT_SET='9092'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

# =========================================================
# System (managed by Websoft9, do not modify)
# =========================================================
W9_ID='kafka'
W9_DB_KAFKA_PORT=9092
W9_NETWORK=websoft9
#### --------------------------------------------------------------------------------------- ####

# =========================================================
# Application-specific settings
# Official environment variable reference: https://github.com/bitnami/containers/tree/main/bitnami/kafka
# =========================================================
KAFKA_CFG_NODE_ID=0
KAFKA_CFG_PROCESS_ROLES=controller,broker
KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093
KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@$W9_ID:9093
KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER
```

#### Step 3d: 生成后验证

```
✅ .env 检查清单:
  [✅/❌] W9_REPO 值与 research_data.basic_info.image 一致
  [✅/❌] W9_VERSION 为具体版本号（非 latest）
  [✅/❌] W9_ID 值为 '{app_name}'
  [✅/❌] W9_NETWORK=websoft9
  [✅/❌] 分隔线格式正确
  [✅/❌] W9_LOGIN_* 与 confirmed_decisions 一致
  [✅/❌] W9_URL_REPLACE 与 confirmed_decisions 一致
  [✅/❌] 所有密码引用 $W9_POWER_PASSWORD
  [✅/❌] 无空值变量（除 W9_URL 外）
```

---

### Phase 4: 生成 docker-compose.yml

**操作：** 基于阶段 2 Step 4d 的完整 compose 预览生成文件

#### Step 4a: 生成基本原则

```
核心原则:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 从阶段 2 批准的 compose 预览直接生成
2. 不重新设计架构或改造方案
3. 只做必要的格式调整（缩进、注释等）
4. 确保 .env 中定义的变量在 compose 中正确引用
```

#### Step 4b: 必须包含的标准元素

```yaml
# 文件头注释（必须）
# image,docs: {dockerhub_or_docs_url}

# 版本声明（如果需要）
version: '3.8'

services:
  # 主服务（必须）
  {app_name}:
    image: $W9_REPO:$W9_VERSION
    container_name: $W9_ID
    restart: unless-stopped
    ports:
      - $W9_HTTP_PORT_SET:{internal_port}
    # env_file 或 environment (取决于变量数量)
    # volumes (取决于计划)

  # 数据库服务（如果有）
  {app_name}-{db}:
    image: {db_image}:{db_version}
    container_name: $W9_ID-{db}
    restart: unless-stopped
    # ...

# 命名卷（如果有）
volumes:
  {volume_definitions}

# 网络（必须）
networks:
  default:
    name: ${W9_NETWORK}
    external: true
```

#### Step 4c: 变量引用规则

```
.env 变量在 compose 中的引用方式:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

方式 1: env_file（推荐，变量较多时）
  env_file: .env
  → .env 中所有变量自动注入容器环境

方式 2: environment 字段（显式引用）
  environment:
    DB_HOST: $W9_ID-mysql
    DB_PASSWORD: $W9_POWER_PASSWORD
  → 明确指定哪些变量传入容器

方式 3: ${VAR} 在 compose 层面插值
  image: $W9_REPO:$W9_VERSION
  container_name: $W9_ID
  ports:
    - $W9_HTTP_PORT_SET:80
  → compose 解析时替换，不进入容器环境

选择原则:
  - 主服务变量 >5 个 → 使用 env_file: .env
  - 数据库服务 → 使用 environment 显式列出
  - W9_ID、W9_REPO 等 → compose 层面 ${} 引用
```

#### Step 4d: 网络配置规范

```yaml
# ⚠️ 关键：网络配置必须使用以下格式（不是 networks: websoft9）
networks:
  default:
    name: ${W9_NETWORK}
    external: true

# ❌ 错误格式（不要使用）
networks:
  websoft9:
    external: true
# 然后在服务中指定 networks: [websoft9]

# ✅ 正确格式使用 default 网络别名 + name 指定
# 这样服务不需要显式声明 networks，自动加入 default
```

#### Step 4e: 生成后验证

```
✅ compose 检查清单:
  [✅/❌] 文件头有注释链接
  [✅/❌] 所有服务有 container_name（使用 $W9_ID 前缀）
  [✅/❌] 所有服务有 restart: unless-stopped
  [✅/❌] 主服务端口使用 $W9_HTTP_PORT_SET
  [✅/❌] 网络配置: default + name: ${W9_NETWORK} + external: true
  [✅/❌] 所有 ./src/ 卷映射的文件将在 Phase 5 创建
  [✅/❌] 环境变量与 .env 一致（无遗漏、无冲突）
  [✅/❌] 数据库密码引用 $W9_POWER_PASSWORD
  [✅/❌] YAML 语法有效（缩进正确、无制表符）
```

---

### Phase 5: 创建 src/ 配置文件

**操作：** 基于阶段 2 Phase 5 的文件规划，创建所有配置文件

#### Step 5a: 确认文件清单

```
从 app-plan.md 提取 src/ 文件列表:

序号 | 文件名            | 映射目标                      | 内容来源
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1    | src/{file1}       | {container_path_1}            | {来源: 官方仓库/文档/默认}
2    | src/{file2}       | {container_path_2}            | {来源}
...  | ...               | ...                           | ...
N    | src/README.md     | (不映射，仅文档)               | 自动生成
```

#### Step 5b: 配置文件内容获取策略

```
获取优先级: (由高到低)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 官方 Git 仓库中的默认配置
   → 从 fork_url 或官方仓库获取原始配置文件
   → 适当修改为 docker-library 环境所需

2. 官方文档的示例配置
   → 从官方文档提取推荐配置
   → 确保版本与 W9_VERSION 匹配

3. 从运行中容器提取
   → docker run --rm {image} cat {config_path}
   → 获取容器内默认配置作为基础

4. 最小可用配置
   → 手动编写满足应用启动的最小配置
   → 在文件内添加注释说明各配置项

⚠️ 注意事项:
  - 配置文件必须能让应用正常启动（开箱即用）
  - 不要包含硬编码的密码或敏感信息
  - 使用 $W9_* 变量引用（如果配置格式支持环境变量）
  - 添加注释帮助用户理解配置
```

#### Step 5c: 生成 src/README.md

```markdown
# Configuration Files

This directory contains custom configuration files mounted into containers.

## Files

| File | Mounted To | Purpose |
|------|-----------|---------|
| {file1} | {container_path_1} | {brief_purpose} |
| {file2} | {container_path_2} | {brief_purpose} |

## Notes

- Changes require container restart: `docker compose restart`
- Backup files before modification
```

#### Step 5d: 特殊情况处理

```
情况 1: 无需 src/ 配置文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 仍然创建 src/ 目录
  → 创建 src/README.md 说明无需配置文件
  → 不创建空的配置文件

情况 2: 配置文件内容无法确定
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 创建文件，写入最小可用配置
  → 在 Notes.md 中标记为"需要在测试阶段验证"
  → 添加 TODO 注释

情况 3: 初始化脚本（如 wordpress 的 init.sh）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  → 脚本文件需要可执行权限
  → 在 compose 中使用 chmod +x 或 entrypoint 处理
  → 确保脚本中的变量引用正确
```

#### Step 5e: 生成后验证与清理

```
✅ src/ 检查清单:
  [✅/❌] 所有 compose 中 ./src/ 卷映射对应的文件已创建
  [✅/❌] 每个配置文件内容非空且格式正确
  [✅/❌] src/README.md 已创建且列出所有文件
  [✅/❌] 无多余文件（compose 中未引用的）  ← 必须二次确认！
  [✅/❌] 脚本文件有适当注释

⚠️ 关键清理步骤（二次确认，此处完成 Phase 2b 推迟的 src/ 清理）:
  - 对照 docker-compose.yml 中 volumes 的 ./src/ 映射
  - 删除所有 src/ 中 compose 未引用的文件（除 README.md 外）
  - 常见模板残留: nginx-proxy.conf.template, php_exra.ini
  - 验证命令:
    ```bash
    cd apps/{app_name}
    for f in src/*; do
      [ "$(basename $f)" = "README.md" ] && continue
      grep -q "$(basename $f)" docker-compose.yml || rm -f "$f" && echo "已删除残留: $f"
    done
    ```
```

---

### Phase 6: 生成 variables.json

**操作：** 生成 README 模板变量文件

#### Step 6a: 正确的 variables.json 格式

⚠️ **关键：** variables.json 只包含以下字段，不要添加任何其他字段。
参考真实应用的格式（wordpress、gitlab、nginx 均使用此结构）。

```json
{
  "name": "{app_name}",
  "trademark": "{Official Trademark}",
  "release": true,
  "fork_url": "{official_git_repo_url}",
  "version_from": "{dockerhub_tags_url}",
  "edition": [
    {
      "dist": "community",
      "version": [
        "{specific_version}",
        "latest"
      ]
    }
  ],
  "requirements": {
    "cpu": "{min_cpu_cores}",
    "memory": "{min_memory_gb}",
    "disk": "{min_disk_gb}",
    "url": "{requirements_doc_url}"
  }
}
```

#### Step 6b: 字段填写规则

```
字段说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

name:
  ✅ 小写，与目录名一致: "wordpress", "gitlab", "nginx"
  ❌ 不要大写: "WordPress", "GitLab"

trademark:
  ✅ 官方商标名称: "WordPress", "Gitlab", "NGINX"
  ℹ️ 注意大小写与官方一致

release:
  ✅ 新应用一律设为 true

fork_url:
  ✅ 官方 Git 仓库地址
  📌 Docker Official Image: https://github.com/docker-library/{name}
  📌 Verified Publisher: 官方 GitHub 仓库
  📌 Community: 镜像构建仓库

version_from:
  ✅ Docker Hub tags 页面 URL
  📌 Docker Official: https://hub.docker.com/_/{name}/tags
  📌 其他: https://hub.docker.com/r/{org}/{repo}/tags

edition:
  ✅ dist: 通常为 "community"
  ✅ version: ["{具体版本}", "latest"]
  ✅ 版本号与 .env 中 W9_VERSION 一致

requirements:
  ✅ cpu/memory/disk 为字符串格式的数字
  ✅ 默认最低: cpu="1", memory="1", disk="1"
  ✅ 复杂应用根据官方文档调整 (如 gitlab: cpu=2, memory=8, disk=10)
  ✅ url: 官方系统需求文档链接
```

#### Step 6c: 真实应用参考

```json
// nginx (简单应用)
{
  "name": "nginx",
  "trademark": "NGINX",
  "release": true,
  "fork_url": "https://github.com/nginxinc/docker-nginx",
  "version_from": "https://hub.docker.com/_/nginx/tags",
  "edition": [{"dist": "community", "version": ["1.29", "latest"]}],
  "requirements": {"cpu": "1", "memory": "1", "disk": "1",
    "url": "https://github.com/nginx/docker#recommended-system-requirements"}
}

// gitlab (复杂应用)
{
  "name": "gitlab",
  "trademark": "Gitlab",
  "release": true,
  "fork_url": "https://github.com/gitlabhq/omnibus-gitlab",
  "version_from": "https://hub.docker.com/r/gitlab/gitlab-ce/tags",
  "edition": [{"dist": "community", "version": ["18.1.3-ce.0", "latest"]}],
  "requirements": {"cpu": "2", "memory": "8", "disk": "10",
    "url": "https://github.com/gitlab/docker#recommended-system-requirements"}
}
```

#### Step 6d: 生成后验证

```
✅ variables.json 检查清单:
  [✅/❌] JSON 语法有效
  [✅/❌] name 值与目录名一致
  [✅/❌] 只包含规范字段（name, trademark, release, fork_url, version_from, edition, requirements）
  [✅/❌] 无多余字段（description, tagline, overview, key_features, services, documentation 等均不应出现）
  [✅/❌] version 与 .env 中 W9_VERSION 一致
  [✅/❌] fork_url 和 version_from 为有效 URL
```

---

### Phase 7: 生成 CHANGELOG.md + Notes.md

#### Step 7a: 生成 CHANGELOG.md

```markdown
# CHANGELOG

## Release
### Fixes and Enhancements


```

> ℹ️ **CHANGELOG.md 定位：** 记录 **Websoft9 开发者**对此应用 Docker Compose 配置的变更
> （如版本升级、配置修改、Bug 修复），而**不是**应用本身的发行说明。
> 新应用一律使用空的初始模板。后续由开发者在修改时填写，例如：
> ```
> ### 3.4 → 3.5
> - Updated debezium/server image to 3.5
> - Added Redis offset storage option
> ```

#### Step 7b: 生成 Notes.md

Notes.md 的定位是 **应用使用注意事项** — 记录使用此应用过程中需要特别注意的操作要点。

❌ **不要** 在 Notes.md 中写入：
- `W9_LOGIN_USER` / `W9_LOGIN_PASSWORD` 的有无决策及原因
- `W9_URL_REPLACE` 的包含/排除原因
- 其他 Websoft9 内部配置决策（这些是实现细节，不属于使用者关心的范围）

✅ **应该** 写入的内容：
- 应用使用要点（容器路径、关键配置方式、前置条件）
- 常见问题 FAQ（用户在使用中容易遇到的问题及解答）
- 特殊操作说明（如何切换配置、如何恢复数据等）

**参考格式（灵活，不必过度结构化）：**

```markdown
# {Application Name}

{一句话说明应用的关键使用特征}

## 要点

* {使用前必须知道的事项 1}
* {使用前必须知道的事项 2}
* {关键操作注意事项}

## FAQ

#### {常见问题 1}？

{解答}

#### {常见问题 2}？

{解答}
```

> ℹ️ 参考仓库中真实的 Notes.md:
> - **grafana**: 容器路径、配置格式说明、FAQ（数据库配置、缓存、组合产品）
> - **gitea**: 初始化说明、SSH 端口特征、配置文件处理方式
> - **nginx**: 仅标题（极简应用无需多写）
> 格式灵活务实，信息量与应用复杂度匹配。不要为简单应用强加繁重结构。

#### Step 7c: 生成后验证

```
✅ 文档文件检查清单:
  [✅/❌] CHANGELOG.md 已创建，格式正确
  [✅/❌] Notes.md 已创建，记录关键决策
  [✅/❌] Notes.md 中引用的 URL 有效
```

---

### Phase 8: 文件完整性验证

**操作：** 全面验证所有生成文件的完整性和一致性

#### Step 8a: 文件清单核对

```
📋 文件完整性检查（对照阶段 2 Phase 7b 清单）

序号 | 文件                              | 状态     | 备注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1    | apps/{app_name}/                  | [✅/❌]  | 目录
2    | apps/{app_name}/.env              | [✅/❌]  | {line_count} 行
3    | apps/{app_name}/docker-compose.yml | [✅/❌] | {service_count} 服务
4    | apps/{app_name}/src/              | [✅/❌]  | 目录
{for each src_file}
5    | apps/{app_name}/src/{filename}    | [✅/❌]  | {file_size}
{end}
N    | apps/{app_name}/src/README.md     | [✅/❌]  | 配置说明
N+1  | apps/{app_name}/variables.json    | [✅/❌]  | JSON 有效
N+2  | apps/{app_name}/CHANGELOG.md      | [✅/❌]  | 初始模板
N+3  | apps/{app_name}/Notes.md          | [✅/❌]  | 开发备注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: {total_files}/{expected_files} 文件已创建
```

#### Step 8b: 交叉引用验证

```
🔗 交叉引用检查

1. .env ↔ docker-compose.yml:
   [✅/❌] compose 中引用的所有 $变量 在 .env 中有定义
   [✅/❌] .env 中定义的变量在 compose 中有使用（无冗余变量）
   [✅/❌] 端口映射与 W9_HTTP_PORT_SET / W9_HTTP_PORT 一致

2. docker-compose.yml ↔ src/:
   [✅/❌] 所有 ./src/* 卷映射对应 src/ 目录中的实际文件
   [✅/❌] 无孤立的 src/ 文件（compose 中未引用的）

3. .env ↔ variables.json:
   [✅/❌] W9_VERSION 值一致
   [✅/❌] W9_REPO 与 edition 中的镜像对应

4. confirmed_decisions ↔ 实际文件:
   [✅/❌] W9_LOGIN_* 决策正确执行（有或无）
   [✅/❌] W9_URL_REPLACE 决策正确执行（有或无）
```

#### Step 8c: 语法验证

```
📝 语法检查

[✅/❌] docker-compose.yml: YAML 语法有效
  → 使用 docker compose config 验证（或 YAML 解析器）

[✅/❌] variables.json: JSON 语法有效
  → 使用 JSON 解析器验证

[✅/❌] .env: 环境变量格式正确
  → 无空行导致的解析问题
  → 变量名=值 格式正确
  → 引号使用一致（单引号）

[✅/❌] src/ 配置文件: 格式正确
  → 各文件按其格式（ini/yaml/json/conf 等）验证语法
```

#### Step 8d: 问题修正

```
如果发现问题:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. 记录问题详情
  2. 立即修正
  3. 重新验证修正后的文件
  4. 在 Notes.md 中记录修正内容

如果问题无法自动修正:
  → 在开发报告中标记为 ⚠️ 待处理
  → 建议在测试阶段（Phase 4）验证
```

---

### Phase 9: 开发报告与阶段切换

#### Step 9a: 生成开发报告

```
╔════════════════════════════════════════════════════════════╗
║        ✅ 开发阶段完成 - {app_name}                        ║
╚════════════════════════════════════════════════════════════╝

📁 生成文件
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ .env                    ({line_count} 行, {var_count} 个变量)
✅ docker-compose.yml      ({service_count} 服务)
✅ src/ 目录               ({file_count} 个配置文件)
{for each src_file}
   - src/{filename}
{end}
   - src/README.md
✅ variables.json
✅ CHANGELOG.md
✅ Notes.md

📊 决策执行确认
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
W9_LOGIN_USER/PASSWORD: [✅ 已包含 / ❌ 已排除] — {brief_reason}
W9_URL_REPLACE:         [✅ 已包含 / ❌ 已排除] — {brief_reason}

✅ 验证结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✅/❌] 文件完整: {created}/{expected}
[✅/❌] 交叉引用: 所有引用正确
[✅/❌] 语法验证: 全部通过
[✅/❌] 决策执行: 与 confirmed_decisions 一致

{如果有未解决的问题}
⚠️ 待处理项
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - {issue_description}
{end}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
下一步: 进入阶段 4（测试）

请确认:
[Y] 进入测试阶段
[M] 需要调整 → 说明修改内容
[N] 暂停     → 保存状态
```

#### Step 9b: 处理用户反馈

**Y（进入测试）：**
```json
// 更新 state.json
{
  "stage_status": {
    "research": "completed",
    "analysis": "completed",
    "development": "completed"
  },
  "development_data": {
    "files_created": [
      "apps/{app_name}/.env",
      "apps/{app_name}/docker-compose.yml",
      "apps/{app_name}/src/{...}",
      "apps/{app_name}/src/README.md",
      "apps/{app_name}/variables.json",
      "apps/{app_name}/CHANGELOG.md",
      "apps/{app_name}/Notes.md"
    ],
    "validation_passed": true,
    "issues": []
  }
}
```
→ 加载 `step-04-testing.md`

**M（调整）：**
- 根据用户反馈修改对应文件
- 重新运行 Phase 8 验证
- 再次展示开发报告

**N（暂停）：**
```
⏸️ 工作流已暂停

已生成的文件保留在: apps/{app_name}/
状态已保存: _bmad-output/workflows/{app_name}/state.json

恢复命令: [CA] Create App → 从开发阶段继续
```

---

## 异常处理

### 计划数据缺失或不完整

```
问题: app-plan.md 中的预览内容不完整
处理:
  1. 检查阶段 2 输出的具体缺失项
  2. 如果是次要内容（如注释）→ 根据研究数据补充
  3. 如果是核心内容（如 compose 结构）→ 暂停，提示返回阶段 2
```

### 配置文件内容无法获取

```
问题: src/ 文件的默认内容无法从官方来源获取
处理:
  1. 尝试从运行中的容器提取: docker run --rm {image} cat {path}
  2. 创建最小可用配置 + TODO 注释
  3. 在 Notes.md 中标记"需要在测试阶段优化"
  4. 在开发报告中标注为 ⚠️ 待处理
```

### 复杂多容器应用

```
问题: 服务数量 >5，文件生成复杂
处理:
  1. 严格按阶段 2 计划逐个服务生成
  2. 每个服务生成后立即验证
  3. 最后做全局交叉引用检查
  4. 如果发现计划遗漏 → 记录但不擅自添加，在报告中标注
```
