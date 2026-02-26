# 阶段 2：分析与计划（Analysis）

## 目标

**基于阶段 1 研究数据，生成可执行的应用开发计划文档。**

核心任务：
1. **验证研究结论** — 复核 W9_* 变量决策的合理性
2. **设计 compose 改造方案** — 将官方配置转换为 docker-library 规范
3. **生成文件清单** — 明确需要创建的每个文件及其内容规格
4. **评估风险与工作量** — 预判开发难点

## 执行原则

- 📋 **计划先行**：不生成任何应用文件，只生成计划文档
- 🔄 **对比驱动**：每个改造点都展示"官方 → 改造"对比
- ⚠️ **风险前置**：不确定的决策明确标注，让用户决策
- ⏸️ **用户确认**：必须获得用户批准才能进入开发阶段

---

## 前置条件

✅ 阶段 1 研究完成（state.json 中 `research.completed = true`）
✅ 研究数据 `research_data` 已加载
✅ 信息完整度 ≥ 50%

---

## 分析流程

### 流程概览

```
Phase 1  → 加载并验证研究数据
Phase 2  → 容器架构设计 (服务列表 + 依赖关系)
Phase 3  → .env 文件规划 (变量映射 + W9_* 决策确认)
Phase 4  → docker-compose.yml 改造设计 (官方 → 规范)
Phase 5  → src/ 文件与卷映射规划
Phase 6  → 测试策略制定
Phase 7  → 风险评估与开发清单
Phase 8  → 生成计划文档 + 用户确认
```

---

### Phase 1: 加载并验证研究数据

**操作：** 读取 `_bmad-output/workflows/{app_name}/state.json`

**验证清单：**
```
✅ 核心数据检查:
  [✅/❌] research_data.basic_info.image 非空
  [✅/❌] research_data.basic_info.version 非空
  [✅/❌] research_data.architecture.service_count > 0
  [✅/❌] research_data.compliance_prediction 存在

⚠️ 置信度检查:
  W9_LOGIN_* 置信度: {confidence}% [≥85% 自动采纳 / <85% 标记需确认]
  W9_URL_REPLACE 置信度: {confidence}% [≥85% 自动采纳 / <85% 标记需确认]
```

**输出：**
```
🔄 分析阶段开始

应用: {app_name}
镜像: {image}:{version} ({image_source})
复杂度: {level} ({score}/100)
信息完整度: {percentage}%

正在生成应用开发计划...
```

---

### Phase 2: 容器架构设计

**目标：** 将研究中发现的服务转换为 docker-library 规范架构

**⚠️ 模式匹配（首先执行）：**
```
读取: _bmad/bmb/knowledge/app-patterns.yaml

根据研究数据执行模式匹配:
  服务数={service_count}, 有DB={has_db}, 有缓存={has_cache}, 有共享网络={has_shared_net}
  
  → 匹配到: Pattern {id} - {name}
  → 加载: compose_skeleton 作为架构设计起点
  → 参考应用: {reference_apps}
  → 保存到: state.json.matched_pattern = "{pattern_id}"

💡 与从白纸设计相比，先加载骨架再基于官方 compose 差分调整效率更高
```

**🔍 相似应用自动检查（匹配后执行）：**
```
从匹配模式的 representative_apps 中选取最相似的 1 个应用进行deep inspect。

选取规则:
  优先级 1: 同类型应用（如同为 CMS → 选 wordpress，同为 DevTool → 选 gitea）
  优先级 2: 服务数最接近的应用
  优先级 3: 模式中列出的第一个 representative app

执行检查（并行读取）:
  read_file: apps/{similar_app}/.env
  read_file: apps/{similar_app}/docker-compose.yml
  read_file: apps/{similar_app}/variables.json

提取参考信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  参考应用: {similar_app}
  
  .env 结构:
    W9 标准变量: {列出所有 W9_ 变量}
    应用专属变量: {列出分隔线以下的变量}
    W9_LOGIN: {有/无} → 证据: {变量名}
    W9_URL_REPLACE: {有/无}
  
  compose 结构:
    服务数: {n}
    网络模式: {bridge/host/service:xxx}
    healthcheck: {有/无, 哪些服务}
    volumes 模式: {named volumes / bind mounts / src/ 文件}
  
  variables.json:
    字段列表: {列出所有字段名，作为新应用的参考}
  
  ⚠️ 差异标记:
    {列出新应用与参考应用的关键差异}
    例如: "参考应用 wordpress 使用 MySQL，新应用使用 PostgreSQL"
    例如: "参考应用有 W9_LOGIN，新应用不需要（原因: setup wizard）"

💡 用途: 直接复用参考应用的文件结构，只修改差异部分，避免从零构建
```

**⚠️ 架构来源验证：**
```
检查 state.json 中的架构决策来源:

[情况 1] Compose 类型 A (产品级) + 无用户覆盖
  → 以模式骨架为底，用官方 compose 架构覆盖差异部分

[情况 2] Compose 类型 B (Demo) + 用户已在 Step 10g 选择方案
  → 使用用户选择的方案 (从 state.json architecture_decision.user_choice 读取)
  → 如果 state.json 中无 user_choice → 🚨 停止，返回 step-01 Phase 10g 请用户确认

[情况 3] Compose 类型 C (最小化) 或无官方 compose
  → 以模式骨架为基准设计架构，Phase 8 中提请用户确认
```

**设计规则：**

```
容器命名规范:
  主服务:   container_name: $W9_ID
  依赖服务: container_name: $W9_ID-{service_name}
  
  示例:
    wordpress    → $W9_ID        (即 wordpress)
    mysql        → $W9_ID-mysql  (即 wordpress-mysql)
    redis        → $W9_ID-redis  (即 wordpress-redis)

网络规范:
  所有应用使用外部网络:
  networks:
    default:
      name: ${W9_NETWORK}
      external: true

端口规范:
  主 HTTP 端口: ${W9_HTTP_PORT_SET}:{容器内部端口}
  额外端口:     ${W9_XXX_PORT_SET}:{容器内部端口}
```

**输出格式：**
```
📊 容器架构设计

服务拓扑:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  {app_name} (主服务)
  ├── image: $W9_REPO:$W9_VERSION
  ├── container_name: $W9_ID
  ├── ports: $W9_HTTP_PORT_SET:{internal_port}
  ├── restart: unless-stopped
  └── depends_on: [{依赖列表}]

  {db_service} (数据库)  [如果有]
  ├── image: {db_image}:{db_version}
  ├── container_name: $W9_ID-{db_name}
  └── volumes: {db_name}_data:{容器数据路径}

  {cache_service} (缓存)  [如果有]
  ├── image: {cache_image}:{cache_version}
  └── container_name: $W9_ID-{cache_name}

命名卷:
  - {volume_1}: {用途}
  - {volume_2}: {用途}

复杂度: {service_count} 服务 → {level}
```

---

### Phase 3: .env 文件规划

**目标：** 设计完整的 .env 变量列表，确认所有 W9_* 决策

#### Step 3a: 必需变量（始终包含）

```env
# 版本和仓库信息 (来自研究阶段 Phase 8/9)
W9_REPO={image_name}
W9_VERSION='{version}'
W9_POWER_PASSWORD='{auto_generated}'

# 用户可配置
W9_HTTP_PORT_SET='9001'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####
W9_ID='{app_name}'
W9_HTTP_PORT={internal_port}
W9_URL='{url_format}'
W9_NETWORK=websoft9
```

#### Step 3b: W9_LOGIN_* 决策确认

```
研究阶段结论:
  匹配模式: [{matched_pattern}]
  置信度: {confidence}%
  证据: {evidence}

分析阶段验证:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

检查 1: compose 中是否有管理员环境变量?
  {检查 docker-compose.yml environment 字段}
  → [✅ 有] / [❌ 无]

检查 2: 管理员账户是通过环境变量设置还是首次访问设置?
  → [✅ 环境变量 → 需要 W9_LOGIN_*]
  → [❌ 首次访问 → 不需要]

最终决策: [✅ 包含 / ❌ 排除] W9_LOGIN_USER + W9_LOGIN_PASSWORD
理由: {final_reason}
```

**如果包含 W9_LOGIN_*：**
```env
W9_LOGIN_USER={admin_username}
W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD
```

#### Step 3c: W9_URL_REPLACE 决策确认

```
研究阶段结论:
  匹配模式: [{matched_pattern}]
  置信度: {confidence}%
  证据: {evidence}

分析阶段验证:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

检查 1: docker-compose.yml 中是否引用 $W9_URL?
  {检查 environment 字段中是否包含 $W9_URL}
  → [✅ 有] / [❌ 无]

检查 2: 引用方式是什么?
  → hostname: "$W9_URL"
  → TRUSTED_DOMAINS=$W9_URL
  → EXTERNAL_URL=http://$W9_URL
  → 其他: {具体方式}

检查 3: W9_URL 格式应该是什么?
  → internet_ip:$W9_HTTP_PORT_SET (默认，含端口)
  → appname.example.com (不含端口，用于需要域名的应用)

最终决策: [✅ 包含 / ❌ 排除] W9_URL_REPLACE=true
W9_URL 格式: {选定格式}
理由: {final_reason}
```

#### Step 3d: 应用特定变量

```
来源: 官方 compose 环境变量 + 官方文档

变量映射表:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
官方变量                    →  docker-library 变量
{OFFICIAL_DB_HOST}         →  $W9_ID-{db_name}
{OFFICIAL_DB_PASSWORD}     →  $W9_POWER_PASSWORD
{OFFICIAL_DB_NAME}         →  $W9_ID
{OFFICIAL_DB_USER}         →  $W9_ID
{OFFICIAL_SECRET_KEY}      →  $W9_POWER_PASSWORD 或 自动生成
{其他应用变量}              →  {保留原值或合理默认值}
```

#### Step 3e: 完整 .env 预览

生成完整的 .env 文件内容预览，供用户确认。

⚠️ **格式要求 — 必须遵循 step-03 Phase 3a 标准模板**

此预览将在 step-03 中直接用于生成最终 .env 文件，因此**必须**使用 step-03 Phase 3a 定义的结构化注释格式，而非参照旧应用的简洁格式。

**标准格式要点（完整规范见 step-03 Phase 3a-3c）：**

```
1. 文件头注释（3 行）：
   # {App Name} on Docker - Environment Configuration
   # Edit this file to customize the deployment settings.
   # Full documentation: {official_docs_url}

2. 分节标题用 ========= 注释块：
   # =========================================================
   # Image / Authentication / Ports / System / Application-specific
   # =========================================================

3. 分隔线格式精确：
   #### --  Not allowed to edit below environments when recreate app based on existing data  -- ####

4. 条件裁剪：无认证无数据库时省略 Authentication 节（参照 step-03 条件裁剪规则表）
```

**参考示例：** step-03 中场景 A（WordPress）/ 场景 B（Grafana）/ 场景 C（nginx）/ 场景 D（Kafka）
**仓库实例：** `apps/debezium/.env`（已使用新标准格式）

---

### Phase 4: docker-compose.yml 改造设计

**目标：** 设计从官方 compose 到 docker-library 规范的转换方案

#### Step 4a: 改造规则

```
必须改造的项目:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 镜像引用 → 使用变量
   官方: image: wordpress:6.9
   改造: image: $W9_REPO:$W9_VERSION

2. 容器命名 → 使用 $W9_ID
   官方: container_name: wordpress
   改造: container_name: $W9_ID

3. 端口映射 → 使用变量
   官方: ports: ["8080:80"]
   改造: ports: ["$W9_HTTP_PORT_SET:80"]

4. 网络配置 → 使用外部网络
   官方: (默认 bridge 或自定义网络)
   改造:
     networks:
       default:
         name: ${W9_NETWORK}
         external: true

5. 重启策略 → 统一为 unless-stopped
   官方: restart: always (或无)
   改造: restart: unless-stopped

6. 环境变量 → 使用 env_file + 变量替换
   官方: environment: {硬编码值}
   改造: env_file: .env + environment: {$W9_* 变量}

7. 密码引用 → 统一使用 $W9_POWER_PASSWORD
   官方: MYSQL_PASSWORD: mysecretpassword
   改造: MYSQL_PASSWORD: $W9_POWER_PASSWORD
```

#### Step 4b: 可选改造项

```
根据应用特性选择:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[如果有数据库] 数据库容器名引用
  官方: DB_HOST: db
  改造: DB_HOST: $W9_ID-{db_name}

[如果需要日志限制] 日志配置
  添加:
    logging:
      driver: "json-file"
      options:
        max-file: "5"
        max-size: 10m

[如果有 Swarm 特性] 移除 deploy 配置
  官方: deploy: { replicas: 2, ... }
  改造: (移除整个 deploy 块)

[如果有 build 指令] 转换为预构建镜像
  官方: build: .
  改造: image: {预构建镜像名}:{版本}
  ⚠️ 如果无预构建镜像，标记为风险项

[如果有健康检查] 保留或优化
  保留官方健康检查配置，适当调整超时时间
```

#### Step 4c: 改造对比预览

```
🔄 docker-compose.yml 改造方案

改造项目汇总:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
序号 | 改造内容            | 状态
1    | 镜像变量化           | ✅ 必须
2    | 容器命名规范化       | ✅ 必须
3    | 端口变量化           | ✅ 必须
4    | 外部网络配置         | ✅ 必须
5    | 重启策略             | ✅ 必须
6    | 环境变量替换         | ✅ 必须
7    | 密码统一             | ✅ 必须
8    | {可选项1}           | ⚠️ 可选
9    | {可选项2}           | ⚠️ 可选
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Step 4d: 完整 docker-compose.yml 预览

生成完整的 docker-compose.yml 文件内容预览，标注每处改造。

---

### Phase 5: src/ 文件与卷映射规划

**目标：** 确定 src/ 目录中需要创建的每个文件

```
📁 src/ 文件规划

来源: Phase 8 compose 卷映射 + 应用需求分析
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

卷映射类型分析:

[配置文件映射] → 需要创建 src/ 文件
  {for each config volume}
  文件: src/{filename}
  映射: ./src/{filename}:{container_path}
  来源: {从哪里获取默认内容}
    → 官方仓库 (优先)
    → 官方文档示例
    → 从运行中的容器提取 (docker cp)
    → 手动创建合理默认值
  说明: {文件用途}
  {end}

[数据持久化卷] → 使用命名卷，无需 src/ 文件
  {for each data volume}
  卷名: {volume_name}
  路径: {container_path}
  用途: {数据存储说明}
  {end}

[特殊文件]
  src/README.md → 配置文件说明文档 (始终创建)

文件获取计划:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
文件名              | 获取方式      | 优先级
src/{file1}        | 官方仓库      | 高
src/{file2}        | 容器提取      | 中
src/README.md      | 自动生成      | 必须
```

---

### Phase 6: 测试策略制定

**目标：** 基于复杂度评估制定三层测试计划（L1 自动 + L2 远程部署 + L3 人工功能）

```
🧪 测试策略

测试层级: Tier {A/B/C/D}
级别说明: {tier_description}
预估启动时间: {startup_time} 秒（不含镜像下载）
预估测试超时: {timeout} 秒
测试服务器: {server_id} (来自 test-servers.yaml)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L1 静态验证 (agent 自动执行，无网络):
  - [ ] docker compose config 无语法错误
  - [ ] 所有 volume 映射的 src/ 文件存在
  - [ ] .env 变量引用无缺失（所有 $VAR 在 .env 中有定义）
  - [ ] 容器名、网络名规范符合 W9_* 标准

L2 部署验证 (agent 通过 SSH 在远程服务器执行):
  - [ ] 文件上传到测试服务器
  - [ ] docker compose up -d 成功启动
  - [ ] 所有容器状态 running (docker compose ps)
  - [ ] HTTP 端口响应 (curl http://localhost:$W9_HTTP_PORT_SET)
  - [ ] 响应码: {expected_http_code}
  - [ ] 日志无 FATAL/PANIC 错误
  - [ ] docker compose down -v 清理成功

L3 核心功能验证 (人工在浏览器执行):
  - [ ] 首页/仪表板正常加载
  {for each core_function}
  - [ ] {core_function_description}
  {end}
  - [ ] 无明显 UI 异常或报错

L3 应用特定测试清单:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  基于应用类型生成（列出核心功能，不要求 100% 覆盖）：

  {if has_login}
  - [ ] 登录页面可访问
  - [ ] 管理员凭据有效（W9_LOGIN_USER / W9_LOGIN_PASSWORD）
  - [ ] 成功进入管理后台
  {end}

  {if has_database}
  - [ ] 数据库相关功能正常（如创建内容/记录）
  {end}

  {if is_cms_or_wiki}
  - [ ] 创建一篇文章/页面成功
  {end}

  {if is_devtool}
  - [ ] 创建一个项目/仓库成功
  {end}

  {if is_dashboard}
  - [ ] 仪表板数据加载正常
  {end}

  {application_specific_items - 根据应用特性生成 2-5 项核心功能测试}

特别注意:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  - {specific_test_note_1}
  - {specific_test_note_2}
```

---

### Phase 7: 风险评估与开发清单

#### Step 7a: 风险评估

```
⚠️ 风险矩阵

风险等级: [🟢 低 / 🟡 中 / 🔴 高]

开发风险:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{for each risk}
{risk_level} {risk_description}
  影响: {impact}
  缓解: {mitigation}
{end}

常见风险类型:
  🟡 W9_LOGIN_* 置信度 <85% → 需要在测试中验证
  🟡 W9_URL_REPLACE 置信度 <85% → 需要在测试中验证
  🔴 官方 compose 使用 build 指令 → 需要找到预构建镜像
  🟡 服务数 >5 → 启动时间长，可能需要初始化等待
  🟡 使用 latest 标签 → 需要锁定具体版本号
  🟡 src/ 配置文件内容未确定 → 可能需要从容器提取
```

#### Step 7b: 开发文件清单

```
📋 开发文件清单 (阶段 3 将按此顺序生成)

序号 | 文件                        | 状态   | 说明
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1    | apps/{app}/                 | 目录   | 应用根目录
2    | apps/{app}/.env             | 生成   | 环境变量 ({var_count} 个变量)
3    | apps/{app}/docker-compose.yml | 生成 | 编排文件 ({service_count} 个服务)
4    | apps/{app}/src/             | 目录   | 配置文件目录
{for each src_file}
5    | apps/{app}/src/{filename}   | 生成   | {purpose}
{end}
N    | apps/{app}/src/README.md    | 生成   | 配置文件说明
N+1  | apps/{app}/variables.json   | 生成   | README 模板变量
N+2  | apps/{app}/CHANGELOG.md     | 生成   | 变更日志
N+3  | apps/{app}/Notes.md         | 生成   | 开发备注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: {total_files} 个文件
```

---

### Phase 8: 生成计划文档与用户确认

#### Step 8a: 生成计划文档

**输出路径：** `_bmad-output/workflows/{app_name}/app-plan.md`

使用模板 `_bmad/bmb/workflows/app-curator/templates/app-plan-template.md` 填充所有分析结果。

#### Step 8b: 展示摘要并请求确认

```
╔════════════════════════════════════════════════════════════╗
║        ✅ 应用开发计划已生成 - {app_name}                    ║
╚════════════════════════════════════════════════════════════╝

📋 计划摘要
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
应用: {app_name}
镜像: {image}:{version} ({image_source})
架构: {service_count} 服务 ({services_summary})
复杂度: {level} | 测试: Tier {tier}

📊 关键决策
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
W9_LOGIN_USER/PASSWORD: [✅/❌] {reason_brief} ({confidence}%)
W9_URL_REPLACE:         [✅/❌] {reason_brief} ({confidence}%)
src/ 文件:              {file_count} 个
环境变量:               {env_count} 个 (含 {app_specific_count} 个应用特定)

{如果有置信度 <85% 的决策}
⚠️ 需要确认的决策:
  - {uncertain_decision}: {reason}
    建议: {suggestion}
{end}

📁 文件清单: {total_files} 个文件待生成
⚠️ 风险项: {risk_count} 项 ({risk_summary})
📄 完整计划: _bmad-output/workflows/{app_name}/app-plan.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
请 review 计划文档，选择操作:

[Y] 批准计划 → 进入开发阶段
[M] 需要调整 → 说明具体调整内容
[N] 暂停     → 保存状态，稍后继续
```

#### Step 8c: 处理用户反馈

**Y（批准）：**
```json
// 更新 state.json
{
  "stage_status": { "analysis": "completed" },
  "analysis_data": {
    "plan_document": "_bmad-output/workflows/{app_name}/app-plan.md",
    "user_decision": "approved",
    "confirmed_decisions": {
      "w9_login_user": { "required": true, "confirmed": true },
      "w9_url_replace": { "required": false, "confirmed": true }
    }
  }
}
```
→ 加载 `step-03-development.md`

**M（调整）：**
- 根据用户反馈修改对应 Phase 的分析结果
- 重新生成计划文档
- 再次展示摘要请求确认

**N（暂停）：**
```
⏸️ 工作流已暂停

计划文档已保存: _bmad-output/workflows/{app_name}/app-plan.md
状态已保存: _bmad-output/workflows/{app_name}/state.json

恢复命令: [CA] Create App → 从分析阶段继续
```

---

## 参考信息

### variables.json 规范

```json
{
  "name": "{app_name}",
  "trademark": "{AppDisplayName}",
  "release": true,
  "fork_url": "{github_repo_url}",
  "version_from": "{docker_hub_tags_url}",
  "edition": [
    {
      "dist": "community",
      "version": ["{version}", "latest"]
    }
  ],
  "requirements": {
    "cpu": "{min_cpu}",
    "memory": "{min_memory_gb}",
    "disk": "{min_disk_gb}",
    "url": "{requirements_doc_url}"
  }
}
```

### 复杂度 → 简化建议触发条件

仅在复杂度 ≥ 70 分（复杂/非常复杂）时生成简化建议：

```
完整版（推荐）: 包含所有服务
精简版（可选）: 仅保留核心服务

判断核心服务的标准:
  ✅ 主应用容器 → 始终保留
  ✅ 强依赖数据库 → 保留
  ⚠️ 缓存服务 → 可选（标注性能影响）
  ❌ 监控/日志收集 → 可移除
  ❌ CI/CD Runner → 可移除
```

### 成功标准

- [ ] 计划文档内容完整，覆盖所有开发文件
- [ ] W9_* 决策均有明确理由和证据
- [ ] docker-compose.yml 改造方案逐项列出
- [ ] 用户明确批准（Y）后才进入开发阶段

---

**检查点：** 这是关键决策门户。用户必须 review 并批准计划，才能继续到阶段 3（开发）。
