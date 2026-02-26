# 健康仪表盘工作流

**目标：** 快速展示整个 docker-library 的健康状态概览。

---

## 触发方式

在 agent 交互中输入 `/health` 或选择 `[DB] 健康仪表盘`。

---

## 执行流程

### Phase 1: 快速扫描

```bash
# 统计总量
TOTAL=$(ls -d apps/*/ 2>/dev/null | wc -l)

# 统计有 .env 的应用
HAS_ENV=$(find apps -maxdepth 2 -name ".env" | wc -l)

# 统计有 docker-compose.yml 的应用
HAS_COMPOSE=$(find apps -maxdepth 2 -name "docker-compose.yml" | wc -l)

# 统计有 variables.json 的应用
HAS_VARS=$(find apps -maxdepth 2 -name "variables.json" | wc -l)

# 统计有 README.md 的应用
HAS_README=$(find apps -maxdepth 2 -name "README.md" | wc -l)

# 统计使用 :latest 标签的应用
LATEST_TAG=$(grep -rl ':latest' apps/*/docker-compose.yml 2>/dev/null | wc -l)

# 统计有 healthcheck 的应用
HAS_HEALTHCHECK=$(grep -rl 'healthcheck' apps/*/docker-compose.yml 2>/dev/null | wc -l)

# 统计 W9_LOGIN_USER 使用率
HAS_LOGIN=$(grep -rl 'W9_LOGIN_USER' apps/*/.env 2>/dev/null | wc -l)

# 统计 W9_URL_REPLACE 使用率
HAS_URL_REPLACE=$(grep -rl 'W9_URL_REPLACE' apps/*/.env 2>/dev/null | wc -l)

# 统计缺失 src/ 文件的应用（volume 映射但文件不存在）
MISSING_SRC=0
for app in apps/*/; do
  if [ -f "$app/docker-compose.yml" ]; then
    for vol in $(grep -oP '\./src/[^:]+' "$app/docker-compose.yml" 2>/dev/null); do
      [ ! -e "$app/$vol" ] && MISSING_SRC=$((MISSING_SRC + 1))
    done
  fi
done
```

### Phase 2: 生成仪表盘

```
╔════════════════════════════════════════════════════════════╗
║     📊 Docker Library 健康仪表盘                            ║
║     生成时间: {timestamp}                                   ║
╚════════════════════════════════════════════════════════════╝

📦 应用总量
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  应用目录:        {TOTAL}
  有 .env:         {HAS_ENV}/{TOTAL} ({pct}%)
  有 compose:      {HAS_COMPOSE}/{TOTAL} ({pct}%)
  有 variables:    {HAS_VARS}/{TOTAL} ({pct}%)
  有 README:       {HAS_README}/{TOTAL} ({pct}%)

🔒 安全状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  :latest 标签:    {LATEST_TAG} 个应用 {🔴 if > 0 else ✅}
  有 healthcheck:  {HAS_HEALTHCHECK}/{TOTAL} ({pct}%)
  src/ 文件缺失:   {MISSING_SRC} 处 {🔴 if > 0 else ✅}

📋 规范统计
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  W9_LOGIN_USER:   {HAS_LOGIN}/{TOTAL} ({pct}%)
  W9_URL_REPLACE:  {HAS_URL_REPLACE}/{TOTAL} ({pct}%)

📐 模式分布
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Pattern A (solo_web):      {count} ({pct}%)  ██████████
  Pattern B (web_db):        {count} ({pct}%)  ████████
  Pattern C (web_db_cache):  {count} ({pct}%)  █
  Pattern D (multi_service): {count} ({pct}%)  ███
  Pattern E (shared_net):    {count} ({pct}%)  
  Pattern F (db_middleware):  {count} ({pct}%)  

⚠️ 需关注
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  {if LATEST_TAG > 0}
  🔴 {LATEST_TAG} 个应用使用 :latest 标签
     运行: workflow-batch-ops [CF] 修复
  {end}
  
  {if MISSING_SRC > 0}
  🔴 {MISSING_SRC} 处 src/ 文件缺失（volume 映射断裂）
     运行: workflow-batch-ops [AU] 审计详情
  {end}

  {if HAS_COMPOSE < TOTAL}
  ⚠️ {TOTAL - HAS_COMPOSE} 个应用目录缺少 docker-compose.yml
  {end}

🏥 健康评分: {score}/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  文件完整性: {sub_score}/30
  安全合规:   {sub_score}/30
  规范一致:   {sub_score}/20
  版本管理:   {sub_score}/20
```

### 评分规则

```
文件完整性 (30分):
  compose 覆盖率: {HAS_COMPOSE/TOTAL * 15}
  env 覆盖率:     {HAS_ENV/TOTAL * 10}
  README 覆盖率:  {HAS_README/TOTAL * 5}

安全合规 (30分):
  无 :latest:     {(TOTAL - LATEST_TAG)/TOTAL * 15}
  有 healthcheck: {HAS_HEALTHCHECK/TOTAL * 10}
  无 src/ 缺失:   {max(0, 5 - MISSING_SRC)}

规范一致 (20分):
  W9_ 变量覆盖:   (基于抽样检查)
  命名规范:       (基于抽样检查)

版本管理 (20分):
  有 W9_VERSION:  (基于抽样检查)
  有 CHANGELOG:   (基于抽样检查)
```

---

## 与其他工作流的关联

```
/health → 发现问题 → workflow-batch-ops [AU] 详细审计
                   → workflow-batch-ops [CF] 批量修复
                   → workflow-batch-ops [VU] 批量更新
                   → workflow-fix-app [CF]   单个修复
```
