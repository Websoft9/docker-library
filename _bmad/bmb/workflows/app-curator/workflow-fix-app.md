# 修复/更新应用工作流

**目标：** 快速更新现有应用的版本或修复配置问题，无需重走完整四阶段流程。

---

## 工作流架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  检测变更     │    │  执行更新     │    │  快速验证     │
│  🔍         │───▶│  🔧         │───▶│  🧪         │
└─────────────┘    └─────────────┘    └─────────────┘
    ↓ 输出              ↓ 输出              ↓ 输出
  变更清单           修改后的文件          验证通过
```

耗时预估：5-15 分钟（对比完整 [CA] 流程的 1-2 小时）

---

## 初始化

```
修复/更新模式 — 快速迭代现有应用

请提供:
  1. 应用名称（apps/ 下的目录名）
  2. 操作类型:
     [VU] 版本更新 — 升级到新版本
     [CF] 配置修复 — 修复已知问题
     [RI] 重新生成 — 基于新规范重新生成文件

示例: "wordpress VU" 或 "pangolin CF"
```

---

## 操作类型 [VU] 版本更新

### Phase 1: 版本检测

```
读取: apps/{app_name}/.env

当前版本信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  镜像: {W9_REPO}
  当前版本: {W9_VERSION}
  
检测新版本:
  1. 检查 Docker Hub tags: https://hub.docker.com/r/{W9_REPO}/tags
  2. 检查 GitHub releases (如果有 source repo)
  3. 与用户指定的目标版本确认

显示:
  当前: {W9_REPO}:{current_version}
  最新: {W9_REPO}:{latest_version}
  目标: {W9_REPO}:{target_version}
  
  [U] 更新到 {target_version}
  [S] 跳过
```

### Phase 2: 变更影响分析

```
检查新版本是否有破坏性变更:

1. compose 结构变化:
   → 获取新版本的官方 compose (如果有)
   → diff 对比当前 docker-compose.yml 中的关键字段
   → 标记: [无变化] / [小调整] / [重大变更]

2. 环境变量变化:
   → 检查新版本是否新增/移除/改名环境变量
   → 标记需要更新的 .env 变量

3. 配置文件变化:
   → 检查 src/ 下的配置文件是否需要更新
   → 标记需要修改的文件

变更影响评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [✅ 无破坏性变更] 仅需改 W9_VERSION → 快速更新
  [⚠️ 小范围变更]  需调整少量配置 → 引导式更新
  [🔴 重大变更]    建议用 [CA] 重新创建 → 转到完整流程
```

### Phase 3: 执行更新

**快速更新（仅版本号）：**
```bash
# 修改 .env 中的版本
sed -i "s/^W9_VERSION=.*/W9_VERSION={target_version}/" apps/{app_name}/.env

# 更新 variables.json 中的版本
# python 或 jq 修改 version 字段

# 更新 CHANGELOG.md
# 追加版本更新记录
```

**引导式更新（有配置变更）：**
```
逐个展示需要修改的文件:

1. .env → 展示 diff → 确认修改
2. docker-compose.yml → 展示 diff → 确认修改
3. src/ 文件 → 展示 diff → 确认修改
4. variables.json → 自动更新版本
5. CHANGELOG.md → 追加更新记录
```

### Phase 4: 快速验证

```
执行简化的三层测试:

L1 静态验证:
  - docker compose config --quiet
  - 文件完整性检查

L2 部署验证 (如果有测试服务器):
  - SSH 上传 → compose up → HTTP 测试 → 清理
  - 或本地快速测试

L3 人工验证:
  - 仅在有重大变更时需要
  - 快速更新时跳过
```

### Phase 5: 生成 README 与报告

```bash
# 重新生成 README
python3 build/update_readme.py "{app_name}"
```

```
╔════════════════════════════════════════════════════════════╗
║     📦 版本更新完成 - {app_name}                            ║
╚════════════════════════════════════════════════════════════╝

  {W9_REPO}: {old_version} → {new_version}

修改的文件:
  ✅ .env (W9_VERSION)
  ✅ variables.json (version)
  ✅ CHANGELOG.md (更新记录)
  {如果有} ✅ docker-compose.yml
  {如果有} ✅ src/ 文件
  ✅ README.md (自动重新生成)

🚀 下一步: git add && git commit -m "Update {app_name} to {new_version}"
```

---

## 操作类型 [CF] 配置修复

### Phase 1: 问题识别

```
请描述需要修复的问题:
  - Issue URL (如果有)
  - 错误现象
  - 期望行为

或选择常见修复:
  [1] 端口冲突 → 修改 W9_HTTP_PORT_SET
  [2] 密码不生效 → 检查 W9_POWER_PASSWORD 引用
  [3] 容器启动失败 → 分析 compose 配置
  [4] 配置文件缺失 → 补充 src/ 文件
  [5] 自定义问题 → 描述问题
```

### Phase 2: 诊断

```
自动检查清单:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  变量检查:
    □ W9_LOGIN_USER 是否应该存在 → 对比 decision-precedents.yaml
    □ W9_URL_REPLACE 是否应该存在 → 对比 decision-precedents.yaml
    □ 所有 compose 引用的变量在 .env 中有定义

  文件检查:
    □ volume 映射的所有 src/ 文件存在
    □ docker compose config 语法正确
    
  安全检查:
    □ 无 :latest 标签
    □ 无 privileged 模式
    □ 密码引用 $W9_POWER_PASSWORD
    □ restart: unless-stopped

诊断结果:
  [✅ 无问题] / [⚠️ 发现 {n} 个问题]
```

### Phase 3: 修复

```
对每个发现的问题:

  问题 {n}: {描述}
  位置: {file}:{line}
  修复: {具体修改}
  
  [A] 自动修复
  [M] 手动修复（展示建议后等待用户操作）
  [S] 跳过
```

### Phase 4: 验证

同 [VU] Phase 4。

---

## 操作类型 [RI] 重新生成

```
⚠️ 这将基于当前规范重新生成应用文件

保留的内容:
  - .env 中的用户自定义值
  - src/ 中的自定义配置
  - Notes.md 中的备注

重新生成的内容:
  - docker-compose.yml (基于最新规范模板)
  - variables.json (基于最新字段要求)
  - CHANGELOG.md (追加重新生成记录)
  - README.md (重新生成)

确认重新生成? [Y/N]
```

如果确认 → 按 step-03 Phase 3-8 的逻辑重新生成文件，但跳过研究和分析阶段。

---

## 批量操作扩展

```
未来扩展预留:

[BU] 批量更新 — 升级所有使用特定基础镜像的应用
  输入: "mysql:8.0 → mysql:8.4"
  自动: 扫描所有 compose 中使用 mysql:8.0 的应用 → 逐个执行 [VU]

[BA] 批量审计 — 检查所有应用的合规性
  输出: 健康报告（缺少 healthcheck、使用 :latest、安全问题等）
```
