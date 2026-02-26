# 批量操作工作流

**目标：** 对多个应用执行批量审计、版本更新或合规修复。

---

## 工作流架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  扫描/选择    │    │  批量执行     │    │  汇总报告     │
│  🔍         │───▶│  🔧         │───▶│  📊         │
└─────────────┘    └─────────────┘    └─────────────┘
```

---

## 初始化

```
批量操作模式

请选择操作类型:
  [AU] 全量审计 — 审计所有/指定应用的合规性
  [VU] 批量版本更新 — 升级使用特定基础镜像的所有应用
  [CF] 批量配置修复 — 对多个应用应用同一修复

示例: "AU" 或 "VU mysql:8.0 mysql:8.4"
```

---

## 操作类型 [AU] 全量审计

### Phase 1: 扫描范围确定

```
扫描选项:
  [1] 全部应用 (apps/ 目录下所有)
  [2] 指定模式 (如: 所有 Pattern B 应用)
  [3] 指定列表 (如: wordpress,joomla,drupal)
  [4] 最近修改 (如: 最近 30 天内修改的应用)
```

```bash
# 扫描所有应用
APP_LIST=$(ls -d apps/*/ | cut -f2 -d'/' | sort)
TOTAL=$(echo "$APP_LIST" | wc -l)
echo "共 $TOTAL 个应用待审计"
```

### Phase 2: 逐应用审计

对每个应用执行以下检查（复用 L1 静态验证逻辑）:

```
审计清单（每个应用）:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 文件完整性:
   □ .env 存在且非空
   □ docker-compose.yml 存在且语法正确
   □ variables.json 存在
   □ volume 映射的 src/ 文件全部存在

2. 规范合规:
   □ W9_ID 变量正确
   □ W9_NETWORK=websoft9
   □ 容器名使用 $W9_ID 前缀
   □ restart: unless-stopped
   □ 网络声明 external: true

3. 安全基线:
   □ 无 :latest 标签
   □ 无未记录的 privileged
   □ 密码引用 $W9_POWER_PASSWORD
   □ 数据库服务有 healthcheck

4. W9_* 决策一致性:
   □ W9_LOGIN_USER 存在 → compose 中有对应的管理员变量映射
   □ W9_URL_REPLACE=true → compose 中有 $W9_URL 引用
   □ 无 W9_URL_REPLACE → compose 中无 $W9_URL 引用

5. 版本检查:
   □ W9_VERSION 非空
   □ 镜像标签指定版本号
   □ variables.json 中 version 与 .env 中 W9_VERSION 一致
```

### Phase 3: 生成审计报告

```
╔════════════════════════════════════════════════════════════╗
║     📊 批量审计报告                                        ║
╚════════════════════════════════════════════════════════════╝

扫描范围: {scope}
应用总数: {total}
审计时间: {timestamp}

总览:
  ✅ 完全合规: {pass_count} ({pass_pct}%)
  ⚠️ 有警告:  {warn_count} ({warn_pct}%)
  🔴 有问题:  {fail_count} ({fail_pct}%)

🔴 需修复的应用:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {for each failed_app}
  {app_name}:
    - {issue_1}
    - {issue_2}
  {end}

⚠️ 有警告的应用:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {for each warned_app}
  {app_name}: {warning_summary}
  {end}

常见问题统计:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  :latest 标签:         {count} 个应用
  缺少 healthcheck:     {count} 个应用
  硬编码密码:           {count} 个应用
  src/ 文件缺失:        {count} 个应用
  W9_* 决策不一致:      {count} 个应用
  版本号缺失:           {count} 个应用

💡 建议操作:
  - 使用 [CF] 批量修复常见问题
  - 使用 [VU] 更新过旧版本的应用
```

**报告保存：** `_bmad-output/audit-report-{date}.md`

---

## 操作类型 [VU] 批量版本更新

### Phase 1: 确定更新范围

```
输入格式: "VU {old_image}:{old_tag} {new_image}:{new_tag}"
示例: "VU mysql:8.0 mysql:8.4"
     "VU mariadb:10.11 mariadb:11.4"
```

```bash
# 扫描所有使用指定镜像的应用
grep -rl "{old_image}:{old_tag}" apps/*/docker-compose.yml | \
  sed 's|apps/||; s|/docker-compose.yml||'
```

### Phase 2: 影响评估

```
批量版本更新影响评估:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

镜像: {old_image}:{old_tag} → {new_image}:{new_tag}
受影响应用: {count} 个

  应用名称          当前引用方式           预计影响
  ──────────────────────────────────────────────────
  {for each app}
  {app_name}       {引用位置}            [✅ 仅版本号 / ⚠️ 可能需调整]
  {end}

是否继续? [Y/N]
```

### Phase 3: 逐应用更新

```
对每个受影响的应用:
  1. 调用 workflow-fix-app.md [VU] 流程
  2. 仅执行快速更新（改版本号）
  3. 如发现需要配置调整 → 标记为手动处理
  4. 记录每个应用的更新结果

进度: [{completed}/{total}] 当前: {app_name}
```

### Phase 4: 汇总报告

```
╔════════════════════════════════════════════════════════════╗
║     📦 批量版本更新报告                                     ║
╚════════════════════════════════════════════════════════════╝

{old_image}:{old_tag} → {new_image}:{new_tag}

  ✅ 自动更新成功: {count} 个应用
  ⚠️ 需手动处理:  {count} 个应用
  ❌ 更新失败:     {count} 个应用

详情:
  {for each app}
  [{status}] {app_name}: {detail}
  {end}
```

---

## 操作类型 [CF] 批量配置修复

### Phase 1: 定义修复规则

```
常见批量修复:
  [1] 添加缺失的 healthcheck（所有数据库服务）
  [2] 替换 restart: always → restart: unless-stopped
  [3] 移除所有 :latest 标签（替换为具体版本）
  [4] 自定义 sed/修改规则

选择修复项（可多选）:
```

### Phase 2: 预览变更

```
对每个受影响的应用展示 diff 预览:

{app_name}:
  - restart: always
  + restart: unless-stopped

确认应用修复? [Y/S(skip)/N(abort)]
```

### Phase 3: 执行修复

```
逐应用执行修复 → L1 验证 → 记录结果
失败的应用自动回滚
```

### Phase 4: 汇总报告

格式同 [VU] Phase 4。
