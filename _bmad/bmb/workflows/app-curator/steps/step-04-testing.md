# 阶段 4：测试与验证（Testing）

## 目标

**通过三层测试验证阶段 3 生成的应用文件，确保应用可正常运行。**

核心任务：
1. **L1 静态验证** — agent 自动执行，无网络依赖
2. **L2 部署验证** — agent 通过 SSH 在远程测试服务器执行
3. **L2+ 自动化功能探测** — agent 自动执行，curl 多端点 + docker exec 内容验证
4. **L3 核心功能验证** — 生成 test-checklist.md，人工在浏览器执行
5. **问题诊断与修复** — 发现问题时协助诊断并修复
6. **生成 README** — 测试通过后生成最终文档

## 执行原则

- 🤖 **L1 自动化**：agent 直接执行静态检查，零网络依赖
- 🖥️ **L2 远程执行**：agent 通过 SSH 在测试服务器部署验证，避免本地镜像下载慢的问题
- 👤 **L3 人工验证**：生成清晰的核心功能测试清单，人在浏览器中执行
- 🔄 **失败即修复**：测试失败不是终点，先诊断原因再修复后重试
- 🧹 **清理彻底**：每次测试后必须完全清理远程环境

---

## 前置条件

✅ 阶段 3 开发完成（state.json 中 `development.completed = true`）
✅ 用户已批准开发报告
✅ 应用文件已生成在 `apps/{app_name}/` 目录
✅ `development_data.validation_passed = true`

---

## 测试流程

### 流程概览

```
Phase 1    → 加载测试参数 + 读取服务器配置
Phase 2    → L1 静态验证（agent 本地自动执行）
Phase 3    → L2 部署验证（agent SSH 到远程服务器执行）
Phase 4    → L2 结果分析 + 日志检查
Phase 4.5  → L2+ 自动化功能探测（agent 自动，curl 多端点 + docker exec）
Phase 5    → 问题诊断与修复循环（如有问题）
Phase 6    → L3 核心功能验证（生成 test-checklist.md + 人工执行）
Phase 7    → 清理远程环境
Phase 8    → 生成 README
Phase 9    → 测试报告与工作流完成
```

---

### Phase 1: 加载测试参数与服务器配置

#### Step 1a: 加载测试参数

```
读取: _bmad-output/workflows/{app_name}/state.json

提取关键数据:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
app_name:          {app_name}
complexity_score:   {0-100} (来自 analysis_data)
l3_required:       {true/false} (复杂度 > 50 时为 true)
service_count:     {number}
has_login:         {true/false}
has_url_replace:   {true/false}
files_created:     [...]
pending_issues:    [...]

读取: app-plan.md → 测试策略章节
  L2 测试清单
  L3 核心功能清单
```

#### Step 1b: 加载服务器配置

```
读取: _bmad/bmb/test-servers.yaml

服务器信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
默认服务器:     {default_server}
选中服务器:     {server_id} - {server_name}
地址:          {host}:{port}
用户:          {user}
认证方式:       {auth.method} ({key_file 或 password})
Docker Mirror:  {docker.mirror 或 "直连"}
远程工作路径:    {remote_work_dir}

测试参数:
  部署超时:     {deploy_timeout} 秒
  启动等待:     {startup_wait} 秒
  HTTP 重试:     {http_retries} 次
  自动清理:     {auto_cleanup}
```

**服务器选择逻辑：**
```
1. 默认使用 test-servers.yaml 中的 default_server
2. 如果应用需要访问国际镜像（如 GitHub 插件下载） → 优先用 hk
3. 如果需要测试国内网络兼容性 → 用 cn
4. 如果 test-servers.yaml 不存在或未配置 → 回退到本地测试
5. 询问用户确认服务器选择（如有多台可用）
```

**⚠️ 回退到本地测试：**
```
如果 test-servers.yaml 未配置或服务器不可达:
  提示: "远程测试服务器未配置或不可达，将使用本地 Docker 环境。
         注意：首次拉取镜像可能较慢。"
  → 所有 SSH 命令改为本地 run_in_terminal 执行
  → 测试流程不变，只是执行位置不同
```

---

### Phase 2: L1 静态验证（agent 本地自动执行）

**目标：** 零网络依赖的快速检查，确保文件在发送到服务器前没有基本错误。

#### Step 2a: compose 语法验证

```bash
cd /data/agent/docker-library/apps/{app_name}

# docker compose config 验证（仅检查语法，不拉镜像）
docker compose config --quiet 2>&1
```

**判断：**
```
✅ 无输出 = 语法正确
❌ 有输出 = 语法错误 → 显示错误内容，修复后重试
```

#### Step 2b: 文件完整性验证

```bash
# 检查 volume 映射的所有 src/ 文件是否存在
for vol in $(grep -E '^\s*- \./src/' docker-compose.yml | sed 's/.*- //' | cut -d: -f1); do
  [ -e "$vol" ] && echo "✅ $vol" || echo "❌ MISSING: $vol"
done

# 检查必需文件
for f in .env docker-compose.yml variables.json; do
  [ -f "$f" ] && echo "✅ $f" || echo "❌ MISSING: $f"
done
```

#### Step 2c: .env 变量引用验证

```bash
# 从 docker-compose.yml 提取引用的变量
USED_VARS=$(grep -oP '\$\{?\K[A-Z_][A-Z0-9_]*' docker-compose.yml | sort -u)

# 检查每个变量是否在 .env 中定义
for var in $USED_VARS; do
  grep -q "^${var}=" .env && echo "✅ $var" || echo "⚠️ $var (未在 .env 中定义，可能来自系统环境)"
done
```

#### Step 2d: 安全基线检查

```bash
# 1. 禁止 privileged 模式（除非有记录的豁免原因）
grep -q "privileged: true" docker-compose.yml && \
  echo "🔴 SECURITY: privileged=true 检测到，需要在 Notes.md 中记录豁免原因" || \
  echo "✅ 无 privileged 模式"

# 2. 禁止 :latest 标签（必须指定版本号）
grep -E 'image:.*:latest' docker-compose.yml && \
  echo "🔴 SECURITY: 使用了 :latest 标签，请指定具体版本" || \
  echo "✅ 无 :latest 标签"

# 3. 禁止挂载 docker.sock（除非是容器管理工具）
grep -q "docker.sock" docker-compose.yml && \
  echo "⚠️ SECURITY: docker.sock 挂载检测到，仅容器管理工具允许" || \
  echo "✅ 无 docker.sock 挂载"

# 4. 检查密码硬编码（所有密码应引用 $W9_POWER_PASSWORD）
grep -iE '^\s+\w*PASSWORD\w*:\s*[^$]' docker-compose.yml | \
  grep -vi 'W9_POWER_PASSWORD\|W9_LOGIN_PASSWORD' && \
  echo "⚠️ SECURITY: 检测到硬编码密码值，应使用 \$W9_POWER_PASSWORD" || \
  echo "✅ 密码引用规范"

# 5. 检查 restart 策略（应为 unless-stopped）
INVALID_RESTART=$(grep -E 'restart:\s+(always|on-failure|no)' docker-compose.yml)
[ -n "$INVALID_RESTART" ] && \
  echo "⚠️ restart 策略应为 unless-stopped: $INVALID_RESTART" || \
  echo "✅ restart 策略正确"

# 6. 检查不必要的端口暴露
PORT_COUNT=$(grep -cE '^\s+- .*:\d+' docker-compose.yml 2>/dev/null || echo 0)
[ "$PORT_COUNT" -gt 3 ] && \
  echo "⚠️ SECURITY: 暴露了 $PORT_COUNT 个端口映射，请确认是否都必要" || \
  echo "✅ 端口映射数量合理 ($PORT_COUNT)"
```

**安全问题分级：**
```
🔴 阻塞：privileged=true（无豁免）、:latest 标签 → 必须修复
⚠️ 警告：docker.sock、硬编码密码、多余端口 → 记录到 Notes.md 并评估
✅ 通过：无安全问题
```

#### Step 2e: 合规对比检查

> 将新应用与同模式的现有应用进行对比，确保结构一致性。

```bash
# 从 state.json 获取匹配模式和参考应用
PATTERN=$(cat _bmad-output/workflows/{app_name}/state.json | python3 -c "import json,sys; print(json.load(sys.stdin).get('matched_pattern',''))")
# 从 app-patterns.yaml 获取该模式的 representative apps
```

**对比维度：**
```
合规对比: {app_name} vs {reference_app}（同 Pattern {id}）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

结构对比:
  项目                  新应用              参考应用           判定
  ─────────────────────────────────────────────────────────────
  服务数               {n}                {ref_n}            [✅ 合理 / ⚠️ 差异大]
  W9_LOGIN_USER        {有/无}            {有/无}            [✅ 一致 / ⚠️ 不同→确认原因]
  W9_URL_REPLACE       {有/无}            {有/无}            [✅ 一致 / ⚠️ 不同→确认原因]
  healthcheck          {有/无}            {有/无}            [✅ / ⚠️ 参考有但新应用无]
  src/ 文件数          {n}                {ref_n}            [✅ / ⚠️ 差异显著]
  restart 策略         {policy}           {ref_policy}       [✅ / ⚠️]

.env 变量对比:
  标准变量: {缺失的W9_标准变量}
  分隔线:   {是否有 ##### 分隔线}
  变量总数: {count} (模式典型: {pattern_typical})

异常标记:
  {如果 W9_LOGIN 决策与参考应用不同}
  ⚠️ W9_LOGIN 决策偏离: 新应用={有/无}, 参考={有/无}
     原因: {从 decision-precedents.yaml 获取}
     判定: [✅ 有合理解释 / 🔴 需要复核]

  {如果服务数偏离模式典型值超过 2 倍}
  ⚠️ 服务数偏离: 新应用={n} vs 模式典型={typical}
     判定: [✅ 应用确实需要 / 🔴 可能过度设计]
```

**注意：** 不同模式间不做对比（Pattern A 和 Pattern D 的应用不可比）。
只与同模式的参考应用对比。如果是全新模式（如 Pattern E），跳过此步骤。

#### Step 2f: L1 结果汇总

```
📋 L1 静态验证结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [✅/❌] compose 语法验证
  [✅/❌] volume 映射文件完整
  [✅/❌] 必需文件存在
  [✅/⚠️] 变量引用检查
  [✅/⚠️/🔴] 安全基线检查
  [✅/⚠️] 合规对比检查（vs {reference_app}）

综合: [✅ PASS → 继续 L2 / ❌ FAIL → 修复后重试]
```

**如果 L1 失败（含 🔴 安全阻塞项或合规严重偏离） → 修复后重新执行 Phase 2，不进入 Phase 3。**

---

### Phase 3: L2 部署验证（agent SSH 远程执行）

**目标：** 在远程测试服务器上实际部署应用，验证容器启动和 HTTP 连通性。

#### Step 3a: SSH 连接与环境准备

```bash
# 根据 auth.method 构建 SSH 命令前缀
# method=key:
SSH_CMD="ssh -o StrictHostKeyChecking=no -i {key_file} {user}@{host} -p {port}"
# method=password:
SSH_CMD="sshpass -p '{password}' ssh -o StrictHostKeyChecking=no {user}@{host} -p {port}"

# 测试连接
$SSH_CMD "echo 'SSH 连接成功' && docker --version && docker compose version"
```

**失败处理：**
```
❌ SSH 连接失败 → 检查 host/port/认证信息
❌ Docker 未安装 → 提示用户在服务器上安装 Docker
❌ Compose v2 不可用 → 提示安装
```

#### Step 3b: 上传应用文件

```bash
# 创建远程工作目录
$SSH_CMD "mkdir -p {remote_work_dir}/{app_name}"

# 使用 scp/rsync 上传应用目录
# method=key:
scp -o StrictHostKeyChecking=no -i {key_file} -P {port} -r \
  apps/{app_name}/ {user}@{host}:{remote_work_dir}/{app_name}/
# method=password:
sshpass -p '{password}' scp -o StrictHostKeyChecking=no -P {port} -r \
  apps/{app_name}/ {user}@{host}:{remote_work_dir}/{app_name}/

# 验证上传
$SSH_CMD "ls -la {remote_work_dir}/{app_name}/"
```

#### Step 3c: 远程环境准备

```bash
# 确保 websoft9 网络存在
$SSH_CMD "docker network inspect websoft9 > /dev/null 2>&1 || docker network create websoft9"

# 检查端口可用性
$SSH_CMD "ss -tlnp | grep :{W9_HTTP_PORT_SET} || echo '端口可用'"

# 如果有 Docker mirror 配置
# {仅当 docker.mirror 非空时} → 检查 daemon.json 是否已配置镜像加速
```

#### Step 3d: 远程部署

```bash
# 部署应用
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose up -d" 2>&1
```

> ⚠️ **关键：** 设置充足的 timeout（{deploy_timeout} 秒）。
> 首次拉取镜像可能需要较长时间。**绝不要提前取消。**

#### Step 3e: 等待与容器状态检查

```bash
# 等待启动
echo "等待 {startup_wait} 秒..."
sleep {startup_wait}

# 容器状态检查
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose ps"

# 如果有 healthcheck，检查健康状态
$SSH_CMD "docker inspect --format='{{.State.Health.Status}}' {W9_ID} 2>/dev/null || echo 'no healthcheck'"
```

**检查内容：**
```
容器状态:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  期望: {service_count} 容器
  实际: {running_count} 容器 running

  {for each service}
  [✅/❌] {container_name}: {status}
  {end}
```

#### Step 3f: HTTP 连通性测试

```bash
# HTTP 测试（在远程服务器上 curl localhost）
for i in $(seq 1 {http_retries}); do
  RESPONSE=$($SSH_CMD "curl -sS -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:{W9_HTTP_PORT_SET}" 2>/dev/null)
  echo "第 $i 次: HTTP $RESPONSE"
  [ "$RESPONSE" -ge 200 ] && [ "$RESPONSE" -lt 400 ] && break
  sleep 5
done

# 获取响应内容片段
$SSH_CMD "curl -sS --max-time 10 http://localhost:{W9_HTTP_PORT_SET} 2>/dev/null | head -c 500"
```

**判断标准：**
```
✅ 通过: HTTP 200, 301, 302, 303, 307, 308
⚠️ 需关注: HTTP 401, 403（可能正常，应用要求认证）
❌ 失败: HTTP 000（连接超时）, 404, 500, 502, 503
```

#### Step 3g: 资源消耗检查

```bash
# 获取所有容器的资源使用情况（非流式，快照）
$SSH_CMD "docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}' \
  \$(cd {remote_work_dir}/{app_name} && docker compose ps -q)"
```

**检查标准：**
```
资源消耗:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {for each container}
  {container_name}: CPU {cpu}% / MEM {mem_usage}
  {end}

判断:
  ✅ 正常: 单容器 MEM < 512MB, CPU < 50%（空闲态）
  ⚠️ 偏高: 单容器 MEM 512MB-1GB, CPU 50-80%（记录但不阻塞）
  🔴 异常: 单容器 MEM > 1GB 或 CPU > 80%（空闲态持续高占用需排查）
  
  注意: 启动前几十秒资源使用偏高属正常，应在 startup_wait 后采样
```

#### Step 3h: 启动耗时记录

```bash
# 记录从 compose up 到 HTTP 200 的耗时
# 在 Step 3d 开始时记录 START_TIME
# 在 Step 3f HTTP 成功时记录 END_TIME

echo "启动耗时统计:"
echo "  compose up 开始: {start_timestamp}"
echo "  HTTP 200 达成:   {end_timestamp}"
echo "  总启动耗时:      {delta} 秒"
```

**基准参考（来自 app-patterns.yaml）：**
```
  Pattern A (solo_web):    3-10 秒
  Pattern B (web_db):     10-30 秒
  Pattern C (web_db_cache): 20-60 秒
  Pattern D (multi_service): 30-120 秒
  
  判断:
  ✅ 在基准范围内
  ⚠️ 超过基准 2 倍 → 记录到 Notes.md，但不阻塞
  🔴 超过 5 分钟 → 需要排查（可能是启动依赖、健康检查配置问题）
```

#### Step 3i: 重启持久性测试（可选）

> 此测试验证容器重启后数据是否保留。仅在以下条件时执行：
> - 应用包含数据库服务
> - 应用使用 named volumes 存储数据
> - 非简单静态容器 (Pattern A 除外)

```bash
# 1. 记录当前容器 ID（重启后应保持）
BEFORE=$($SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose ps -q | sort")

# 2. 执行重启
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose restart"

# 3. 等待重新启动
sleep {startup_wait}

# 4. 检查容器状态
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose ps"

# 5. 验证 HTTP 连通恢复
$SSH_CMD "curl -sS -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:{W9_HTTP_PORT_SET}"
```

**检查标准：**
```
重启持久性:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [✅/❌] 所有容器重启后恢复 running 状态
  [✅/❌] HTTP 连通恢复
  [ℹ️]   重启恢复耗时: {seconds} 秒
  
  ⚠️ 数据完整性无法通过 L2 自动验证，如需确认数据持久化，
     应在 L3 人工验证中执行（例如：创建内容 → 重启 → 内容仍在）
```

---

### Phase 4: L2 结果分析与日志检查

#### Step 4a: 日志收集

```bash
# 所有服务日志（最近 100 行）
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose logs --tail=100" 2>&1
```

#### Step 4b: 错误检测

```bash
# 过滤错误（排除常见误报）
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose logs 2>&1 | \
  grep -i 'error\|failed\|exception\|fatal\|panic' | \
  grep -vi 'error_log\|error_page\|error_reporting\|no error\|without error\|errors=0' | \
  head -20"
```

**分类处理：**
```
🔴 致命错误 (FATAL/PANIC): 必须修复 → 进入 Phase 5
🟡 一般错误 (ERROR): 分析是否影响核心功能（启动过程中的临时重试可忽略）
🟢 警告 (WARNING): 记录但不阻塞
```

#### Step 4c: 启动成功指标

```bash
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose logs 2>&1 | \
  grep -i 'ready\|started\|listening\|initialization complete\|server running\|accepting' | \
  tail -10"
```

#### Step 4d: L2 结果汇总

```
🧪 L2 部署验证结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
测试服务器: {server_name} ({host})

  [✅/❌] SSH 连接成功
  [✅/❌] 文件上传完成
  [✅/❌] 容器启动: {running}/{expected} 运行
  [✅/❌] HTTP 连通: {http_code}
  [✅/⚠️] 日志分析: {error_count} 错误
  [✅/⚠️] 资源消耗: 最大 MEM {max_mem}, 最大 CPU {max_cpu}%
  [ℹ️]   启动耗时: {startup_seconds} 秒（基准: {pattern_baseline}）
  {如果执行了重启测试}
  [✅/❌] 重启持久性: 容器恢复 {yes/no}, HTTP 恢复 {yes/no}
  {end}

综合: [✅ PASS → 继续 L2+ / ❌ FAIL → 进入 Phase 5 修复]
```

---

### Phase 4.5: L2+ 自动化功能探测

**目标：** 在 L2 基础连通验证通过后，通过 curl 多端点 + docker exec 自动探测应用核心功能是否可用，减少 L3 人工验证负担。

> ℹ️ L2+ 不依赖浏览器，全部由 agent 通过命令行自动执行。
> 即使 L2+ 某些探测失败，也不阻塞流程，仅标记为 ⚠️ 供 L3 重点关注。

#### Step 4.5a: 页面内容验证

```bash
# 1. 首页内容关键词检查
#    根据 app-introduction.md 确定应用名称/品牌词
RESPONSE=$(curl --noproxy '*' -sS --max-time 10 http://localhost:{W9_HTTP_PORT_SET})
echo "$RESPONSE" | grep -qi "{app_brand_keyword}" && \
  echo "✅ 首页包含品牌关键词" || \
  echo "⚠️ 首页未包含预期关键词 '{app_brand_keyword}'"

# 2. HTML 基本结构验证
echo "$RESPONSE" | grep -q '</html>' && \
  echo "✅ HTML 结构完整" || \
  echo "⚠️ HTML 可能不完整"

# 3. 静态资源可达性（CSS/JS）
for asset in $(echo "$RESPONSE" | grep -oP '(href|src)="\K[^"]+\.(css|js)' | head -3); do
  STATUS=$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost:{W9_HTTP_PORT_SET}${asset}")
  echo "  静态资源 $asset: HTTP $STATUS"
done
```

#### Step 4.5b: 关键端点探测

```bash
# 根据应用类型探测关键路径
# 路径列表从 app-plan.md 测试策略章节获取，或使用通用列表:

ENDPOINTS="/ /api /health /login /register /admin /dashboard"

for ep in $ENDPOINTS; do
  STATUS=$(curl --noproxy '*' -sS -o /dev/null -w '%{http_code}' --max-time 5 \
    http://localhost:{W9_HTTP_PORT_SET}${ep} 2>/dev/null)
  case $STATUS in
    200|301|302|303|307|308) echo "✅ $ep → HTTP $STATUS" ;;
    401|403)                 echo "🔒 $ep → HTTP $STATUS (需认证，正常)" ;;
    404)                     echo "ℹ️ $ep → HTTP 404 (不存在)" ;;
    *)                       echo "⚠️ $ep → HTTP $STATUS" ;;
  esac
done
```

#### Step 4.5c: 应用健康与服务状态（容器内探测）

```bash
# 1. 进程检查 — 确认关键进程在运行
docker exec {W9_ID} sh -c 'ps aux 2>/dev/null || ls /proc/*/cmdline 2>/dev/null | \
  while read f; do echo -n "$f: "; cat "$f" 2>/dev/null | tr "\0" " "; echo; done' \
  | head -20

# 2. 端口监听检查（容器内部视角）
docker exec {W9_ID} sh -c 'ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null || \
  cat /proc/net/tcp' | head -10

# 3. 如果应用有 /health 或 /api/health 端点:
docker exec {W9_ID} sh -c \
  'curl -sS --max-time 3 http://localhost:{W9_HTTP_PORT}/health 2>/dev/null || echo "无 health 端点"'

# 4. 对于有数据库的应用 — 验证 DB 连接:
# docker exec {W9_ID} sh -c '{db_check_command}'
```

#### Step 4.5d: 非 Web 应用的探测策略

> 以下策略适用于不提供 HTTP 接口的应用（如数据库、消息队列、CLI 工具等）。

```bash
# 数据库类应用:
# docker exec {W9_ID} {db_cli} -u {user} -p{password} -e "SELECT 1" 2>/dev/null
# 示例: docker exec mysql mysql -uroot -p$W9_POWER_PASSWORD -e "SELECT 1"

# 消息队列类:
# docker exec {W9_ID} {mq_cli} list queues 2>/dev/null

# CLI 工具类:
# docker exec {W9_ID} {tool} --version
# docker exec {W9_ID} {tool} status

# 通用: 检查主进程是否正常运行（退出码 0）
docker exec {W9_ID} sh -c 'kill -0 1 && echo "✅ PID 1 running" || echo "❌ PID 1 not running"'
```

#### Step 4.5e: L2+ 探测结果汇总

```
🔍 L2+ 自动化功能探测结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  页面内容:
    [✅/⚠️] 品牌关键词: {keyword} {found/not_found}
    [✅/⚠️] HTML 结构完整性
    [✅/⚠️] 静态资源: {loaded}/{total}

  端点探测:
    {for each endpoint}
    [{status_icon}] {path} → HTTP {code}
    {end}

  服务状态:
    [✅/⚠️] 主进程运行中
    [✅/⚠️] 预期端口监听中
    [✅/⚠️/ℹ️] Health 端点: {result}

  L3 重点关注项:
    {列出 L2+ 中标记为 ⚠️ 的项目，供 L3 人工重点检查}

综合: [✅ 探测通过 → Phase 6 / ⚠️ 有关注项 → Phase 6 标注重点]
  注: L2+ 探测失败不阻塞流程，仅作为 L3 参考
```

---

### Phase 5: 问题诊断与修复循环

> ⚠️ 仅在 Phase 3-4 发现问题时执行。如果 L2 全部通过，跳转到 Phase 6。

#### Step 5a: 远程诊断

```bash
# 详细容器状态
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose ps -a"

# 失败容器日志
$SSH_CMD "docker logs {failed_container} 2>&1 | tail -50"

# 容器内部检查
$SSH_CMD "docker inspect {failed_container} --format='{{json .State}}'"
```

```
常见问题诊断表:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

症状                        | 可能原因                | 修复位置
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
容器退出 (Exit 1)           | 配置错误/缺少环境变量   | .env 或 docker-compose.yml
容器不断重启 (Restarting)   | 健康检查失败/启动崩溃   | docker-compose.yml healthcheck
HTTP 000 (连接超时)         | 端口映射错/服务未监听   | docker-compose.yml ports
HTTP 502/503                | 反向代理配置错误        | src/ 配置文件
数据库连接失败              | 密码/主机名/网络问题    | .env 变量
镜像拉取失败                | 镜像名错/网络问题       | .env W9_REPO/W9_VERSION
卷挂载错误                  | src/ 文件缺失/权限      | src/ 目录
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Step 5b: 本地修复 → 重新上传 → 重测

```
修复流程:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. agent 在本地修改文件（.env / docker-compose.yml / src/）
2. 先清理远程环境:
   $SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose down -v"
3. 重新上传修改后的文件
4. 回到 Phase 3d 重新部署
5. 每次修复记录到 Notes.md

⚠️ 最大重试次数: 3 次
```

#### Step 5c: 无法自动修复的情况

```
如果 3 次重试后仍然失败:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 收集完整诊断信息:
   - docker compose ps -a
   - docker compose logs（完整日志）
   - .env 内容
   - docker-compose.yml 关键部分

2. 向用户展示诊断报告:
   "⚠️ 自动修复未成功，需要人工介入"
   - 问题描述
   - 已尝试的修复
   - 建议的下一步

3. 用户选择:
   [R] 手动修复后重试
   [S] 跳过 L2 测试，直接进入 L3 人工验证
   [B] 返回阶段 3 重新生成
```

---

### Phase 6: L3 核心功能验证（人工执行）

**目标：** 生成结构化的测试清单文件，帮助用户（可能不熟悉应用）在浏览器中完成核心功能验证。

> ℹ️ L2 通过后（服务器上容器仍在运行），让用户通过浏览器访问进行功能验证。
> 📄 测试清单保存为文件，而非仅在对话中展示，方便用户随时参考。

#### Step 6a: 生成 test-checklist.md

**生成文件：** `_bmad-output/workflows/{app_name}/test-checklist.md`

**内容数据来源（按优先级）：**
1. `app-plan.md` 测试策略章节的 L3 核心功能清单
2. `app-introduction.md` 中的应用功能描述
3. Stage 1 研究阶段了解到的应用特性
4. L2+ 自动探测中标记为 ⚠️ 的重点关注项

**文件模板：**

```markdown
# {app_name} — L3 核心功能测试清单

> 自动生成于 {date}，基于 Stage 1-2 研究成果
> 测试地址: http://{server_host}:{W9_HTTP_PORT_SET}

## 前置条件

- [ ] 浏览器可访问测试地址
- [ ] L2 部署验证已通过
{如果有 setup wizard}
- [ ] 首次访问需完成设置向导
{end}

{如果 has_login = true}
## 登录信息

| 项目 | 值 |
|------|----|
| 用户名 | {W9_LOGIN_USER} |
| 密码 | {W9_POWER_PASSWORD} |
{end}

## 核心功能测试（3-5 项）

### 测试 1: {功能名称}

**操作步骤:**
1. {具体操作描述}
2. {下一步操作}

**期望结果:**
- {用户应该看到什么}

**备注:** {可选的额外说明}

---

### 测试 2: {功能名称}
... (同上格式)

---

{重复 3-5 个核心测试}

## L2+ 自动探测已覆盖项

以下功能已通过自动化探测验证，无需人工复测：
- [x] {L2+ 中 ✅ 的项目列表}

## L2+ 标记的重点关注项

以下项目在自动探测中标记为 ⚠️，请重点检查：
- [ ] {L2+ 中 ⚠️ 的项目列表}

## 测试结果

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 测试 1 | ☐ 通过 / ☐ 失败 | |
| 测试 2 | ☐ 通过 / ☐ 失败 | |
| ... | | |
```

**核心功能选择原则（3-5 项）：**
```
必选:
  1. 首页/仪表板加载 — 验证应用最基本的可用性
  2. 核心业务功能 — 应用的主要用途（如: CMS 能发文章、备份工具能添加数据库）

按应用类型追加:
  - 有用户系统: 注册/登录流程
  - 有数据管理: 数据创建/查看
  - 有配置界面: 设置页面可访问
  - 有 API: 至少一个 API 端点返回正确格式

不要测试:
  - 复杂的管理功能（如角色权限配置）
  - 第三方集成（如 SMTP、OAuth）
  - 性能或压力场景
```

#### Step 6b: 展示测试指引并等待用户

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
👤 L3 核心功能验证

📄 测试清单已生成: _bmad-output/workflows/{app_name}/test-checklist.md
   （包含 {n} 项核心功能测试，每项都有详细操作步骤和期望结果）

测试地址: http://{server_host}:{W9_HTTP_PORT_SET}

请按照测试清单在浏览器中执行验证，完成后告知结果:

[Y] 全部通过
[P] 部分通过（说明哪些失败）
[F] 全部失败
[S] 跳过（稍后再测）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

#### Step 6c: 处理 L3 结果

```
[Y] 全部通过 → 继续 Phase 7 清理
[P] 部分通过:
  - 记录失败项到 Notes.md
  - 如果是配置问题 → 尝试修复后重测 L2+L3
  - 如果是应用已知限制 → 记录到 Notes.md，继续
[F] 全部失败 → 回到 Phase 5 重新诊断
[S] 跳过 → 标记为 "L3 未验证"，继续 Phase 7
```

---

### Phase 7: 清理远程环境

**操作：** 停止并清理远程测试资源

```bash
# 清理远程容器和卷
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose down -v"

# 等待 5 秒确认清理完成
sleep 5

# 清理验证
$SSH_CMD "cd {remote_work_dir}/{app_name} && docker compose ps -a 2>/dev/null"

# 删除远程测试文件（可选）
$SSH_CMD "rm -rf {remote_work_dir}/{app_name}"
```

**验证结果：**
```
✅ 清理检查:
  [✅/❌] 远程容器已停止并移除
  [✅/❌] 远程卷已清理
  [✅/❌] 远程测试文件已删除
```

---

### Phase 8: 生成 README

**操作：** 使用 build 脚本从模板生成 README.md

#### Step 8a: 执行 README 生成

```bash
# 从项目根目录执行
cd /data/agent/docker-library
python3 build/update_readme.py "{app_name}"
```

> ℹ️ README.md 由 `template/README.jinja2` 模板 + `variables.json` 数据自动生成。
> 不要手动编辑 README.md，它会被自动覆盖。

#### Step 8b: 验证生成结果

```bash
# 确认 README.md 已生成
ls -la apps/{app_name}/README.md
head -20 apps/{app_name}/README.md
```

#### Step 8c: 问题处理

```
如果 README 生成失败:
  1. 检查 variables.json 格式（JSON 语法）
  2. 检查 variables.json 必需字段
  3. 检查 Python 依赖: pip3 install jinja2-cli python-dotenv
  4. 修复后重试
```

---

### Phase 9: 测试报告与工作流完成

#### Step 9a: 生成最终报告

```
╔════════════════════════════════════════════════════════════╗
║        🧪 测试阶段完成 - {app_name}                        ║
╚════════════════════════════════════════════════════════════╝

📊 四层测试结果
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

L1 静态验证 (agent 自动):
  [✅/❌] compose 语法      | docker compose config
  [✅/❌] 文件完整性        | volume 映射 + 必需文件
  [✅/⚠️] 变量引用         | .env 覆盖检查

L2 部署验证 ({server_name}):
  [✅/❌] 容器启动          | {running}/{expected} 运行
  [✅/❌] HTTP 连通         | {http_code}
  [✅/⚠️] 日志分析         | {error_count} 错误

L2+ 自动化功能探测 (agent 自动):
  [✅/⚠️] 页面内容         | 品牌关键词 + HTML 完整性
  [✅/⚠️] 端点探测         | {reachable}/{total} 端点可达
  [✅/⚠️] 服务状态         | 进程 + 端口 + Health

L3 核心功能 (人工验证):
  [✅/⚠️/⏭️] {l3_result}  | {detail}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

README 生成: [✅/❌]
综合结果: [✅ PASS / ⚠️ PARTIAL / ❌ FAIL]

{如果有修复记录}
🔧 修复记录
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  第 {n} 次: {问题描述} → {修复方法}
{end}

📁 最终文件清单
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ apps/{app_name}/.env
✅ apps/{app_name}/docker-compose.yml
✅ apps/{app_name}/src/ ({file_count} 个文件)
✅ apps/{app_name}/variables.json
✅ apps/{app_name}/CHANGELOG.md
✅ apps/{app_name}/Notes.md
✅ apps/{app_name}/README.md (自动生成)
✅ _bmad-output/workflows/{app_name}/test-checklist.md (L3 测试清单)
```

#### Step 9b: 用户确认

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
请确认:

[Y] 完成 → 应用创建流程结束 🎉
[M] 需要修改 → 说明具体问题
[R] 重新测试 → 重跑 L2 测试
[N] 暂停     → 保存状态
```

#### Step 9c: 处理用户反馈

**Y（完成）：**
```json
// 更新 state.json
{
  "stage_status": {
    "research": "completed",
    "analysis": "completed",
    "development": "completed",
    "testing": "completed"
  },
  "test_data": {
    "tier": "{A/B/C/D}",
    "test_server": "{server_id}",
    "l1_result": "PASS",
    "l2_result": "PASS",
    "l3_result": "{PASS/PARTIAL/SKIPPED}",
    "http_code": {code},
    "fix_count": {number},
    "readme_generated": true
  }
}
```

展示完成消息：
```
╔════════════════════════════════════════════════════════════╗
║       🎉 应用创建完成 - {app_name}                         ║
╚════════════════════════════════════════════════════════════╝

📁 应用目录: apps/{app_name}/
📋 完整文件:
   .env / docker-compose.yml / src/ / variables.json
   CHANGELOG.md / Notes.md / README.md

📊 工作流统计:
   阶段 1 研究 ✅ → 阶段 2 分析 ✅ → 阶段 3 开发 ✅ → 阶段 4 测试 ✅

🚀 下一步:
   1. git add apps/{app_name}/ && git commit -m "Add {app_name}"
   2. PR 到 dev 分支 → CI 自动复测 L2
   3. PR 到 main 分支 → 自动同步 Contentful + 生成 README

📖 Issue 追踪: {issue_url}
```

**M（修改）：**
- 根据用户反馈修改相应文件
- 必要时回到 Phase 3 重新远程测试
- 如果修改了 variables.json，重新生成 README

**R（重测）：**
- 清理远程环境（Phase 7）后重新从 Phase 3 开始

**N（暂停）：**
```
⏸️ 工作流已暂停

应用文件: apps/{app_name}/
状态: _bmad-output/workflows/{app_name}/state.json

恢复命令: [CA] Create App → 从测试阶段继续
```

---

## 异常处理

### SSH 连接失败

```
问题: 无法连接远程测试服务器
处理:
  1. 检查 test-servers.yaml 配置（host/port/auth）
  2. 测试: ssh -v {user}@{host} -p {port}
  3. 确认服务器防火墙允许 SSH 连接
  4. 回退方案: 切换到本地测试模式
```

### 镜像拉取失败（远程）

```
问题: 远程服务器拉取镜像失败
处理:
  1. 检查镜像名: grep W9_REPO apps/{app_name}/.env
  2. 如果是国内服务器 → 检查 Docker mirror 配置
  3. 如果是网络问题 → 切换到 hk 服务器重试
  4. 如果镜像不存在 → 返回阶段 3 修改 W9_REPO/W9_VERSION
```

### compose 语法错误

```
问题: docker compose config 或 up 报语法错误
处理:
  1. L1 阶段应已捕获大部分语法错误
  2. 运行时错误: 检查 .env 变量替换结果
  3. 修复 docker-compose.yml 后重新上传
```

### 端口冲突（远程）

```
问题: 远程服务器端口被占用
处理:
  1. 查看: $SSH_CMD "ss -tlnp | grep :{port}"
  2. 方案 A: 清理远程服务器上的残留容器
  3. 方案 B: 修改 .env 中 W9_HTTP_PORT_SET 后重新上传
```
