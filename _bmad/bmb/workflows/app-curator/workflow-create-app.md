---
name: create-app
description: Create new Docker Compose application for docker-library
---

# 创建应用工作流

**目标：** 从 GitHub Issue 开始，通过四阶段流程创建符合 docker-library 规范的生产就绪应用。

---

## 工作流架构

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  阶段 1     │    │  阶段 2     │    │  阶段 3     │    │  阶段 4     │
│  研究与学习 │───▶│  分析与计划 │───▶│  开发与生成 │───▶│  测试与验证 │
│  🔍         │    │  📋         │    │  🏗️         │    │  🧪         │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
    ↓ 输出              ↓ 输出              ↓ 输出              ↓ 输出
 research_data      app-plan.md         应用文件目录        README.md
 + state.json    + confirmed_decisions  apps/{app}/       + 测试报告
```

### 阶段详情

| 阶段 | 文件 | 核心任务 | 检查点 |
|------|------|---------|--------|
| 1. 研究 | step-01-research.md | 从零认识应用 + 研究部署方式 | 信息完整度 ≥ 50% |
| 2. 分析 | step-02-analysis.md | 生成开发计划文档 | **用户必须批准** |
| 3. 开发 | step-03-development.md | 按计划生成所有文件 | 文件完整性验证 |
| 4. 测试 | step-04-testing.md | 部署验证 + 生成 README | **用户确认完成** |

### 核心原则

- **先认识再部署**：先理解应用本身，再研究技术实现
- **官方为基准**：忠于官方 Docker Compose 配置
- **计划先行**：阶段 2 必须生成完整计划并获批准才能写代码
- **用户决策**：机器建议，人工拍板（阶段 2、3、4 都有确认点）
- **失败即修复**：测试失败不是终点，诊断后修复重试

---

## 初始化

### 配置加载

从 `{project-root}/_bmad/bmb/config.yaml` 加载：
- `user_name` — 用户名称
- `communication_language` — 输出语言
- `output_folder` — 工作流数据存储根目录

### 开始工作流

```
创建应用模式：从 GitHub Issue 到生产就绪应用。

我将引导您完成四个阶段：研究 → 分析 → 开发 → 测试。

请提供 GitHub Issue URL：
示例：https://github.com/Websoft9/docker-library/issues/2002
```

等待用户输入 Issue URL。

---

## 执行流程

### 新建应用

收到 Issue URL 后：

1. 验证 URL 格式（`https://github.com/Websoft9/docker-library/issues/\d+`）
2. 读取 Issue 内容，提取应用名称和参考链接
3. 显示确认信息：
   ```
   📋 应用: {app_name}
   🔗 Issue: {issue_url}
   开始阶段 1（研究）...
   ```
4. **加载并执行** `step-01-research.md`

### 恢复中断的工作流

如果检测到已有 state.json（例如用户暂停后恢复）：

```
检查: _bmad-output/workflows/{app_name}/state.json

如果 state.json 存在:
  读取 current_stage 和 stage_status
  
  显示:
  "检测到未完成的工作流：
    应用: {app_name}
    当前阶段: {current_stage}
    进度: Phase {current_phase}/{total_phases}
    已完成 Phase: {completed_phases}
    
    [C] 继续 → 从 Phase {current_phase} 继续
    [R] 重新开始 → 清除状态，从阶段 1 开始
    [V] 查看状态 → 显示详细状态后再选择"
```

恢复跳转规则：
- `research.status = completed, analysis.status = not_started` → 加载 `step-02-analysis.md`
- `analysis.status = completed, development.status = not_started` → 加载 `step-03-development.md`
- `development.status = completed, testing.status = not_started` → 加载 `step-04-testing.md`
- 阶段内中断 → 加载对应阶段文件，从 `current_phase` 恢复（跳过已完成的 Phase）

**Phase 级恢复示例：**
```
如果 research.status = in_progress, research.current_phase = 8:
  → 加载 step-01-research.md
  → Phase 1-7 已完成（读取 phase_outputs 中的缓存数据）
  → 从 Phase 8 继续执行
```

---

## 工作流状态管理

### 状态文件

**路径：** `_bmad-output/workflows/{app_name}/state.json`

```json
{
  "app_name": "{app_name}",
  "issue_url": "{issue_url}",
  "created_at": "{ISO 8601 timestamp}",
  "updated_at": "{ISO 8601 timestamp}",
  "current_stage": "research|analysis|development|testing",
  "matched_pattern": "{pattern_id from app-patterns.yaml}",
  "stage_status": {
    "research": {
      "status": "not_started|in_progress|completed",
      "current_phase": 0,
      "total_phases": 11,
      "completed_phases": [],
      "phase_outputs": {
        "6": { "file": "app-introduction.md", "saved": true },
        "8": { "compose_found": true, "source": "github" },
        "urls_fetched": [],
        "raw_snippets": {}
      }
    },
    "analysis": {
      "status": "not_started|in_progress|completed",
      "current_phase": 0,
      "total_phases": 8,
      "completed_phases": [],
      "phase_outputs": {}
    },
    "development": {
      "status": "not_started|in_progress|completed",
      "current_phase": 0,
      "total_phases": 9,
      "completed_phases": [],
      "phase_outputs": {}
    },
    "testing": {
      "status": "not_started|in_progress|completed",
      "current_phase": 0,
      "total_phases": 9,
      "completed_phases": [],
      "phase_outputs": {}
    }
  },
  "research_data": {
    "basic_info": { "image": "", "version": "", "image_source": "" },
    "architecture": { "service_count": 0, "services": [], "ports": [] },
    "official_compose": { "raw_content": "", "source_url": "" },
    "compliance_prediction": {},
    "completeness": 0
  },
  "analysis_data": {
    "plan_document": "_bmad-output/workflows/{app_name}/app-plan.md",
    "user_decision": "approved|pending",
    "confirmed_decisions": {
      "w9_login_user": { "required": false, "value": "", "confirmed": false, "rule_id": "" },
      "w9_url_replace": { "required": false, "confirmed": false, "rule_id": "" }
    }
  },
  "development_data": {
    "files_created": [],
    "validation_passed": false,
    "issues": []
  },
  "test_data": {
    "tier": "",
    "test_server": "",
    "l1_result": "",
    "l2_result": "",
    "l3_result": "",
    "http_code": 0,
    "fix_count": 0,
    "security_issues": [],
    "readme_generated": false
  }
}
```

**Phase 追踪规则：**
- 每个 Phase 完成后：`completed_phases` 追加当前 phase 编号，`current_phase` 递增
- 恢复时：跳过 `completed_phases` 中的 Phase，从 `current_phase` 继续
- `phase_outputs` 缓存关键中间结果，避免重复执行已完成的 Phase

### 工作流产出文件

```
_bmad-output/workflows/{app_name}/
├── state.json                    ← 工作流状态（所有阶段共享）
├── app-introduction.md           ← 阶段 1: 应用认知总结
├── official-compose.yml          ← 阶段 1: 官方 compose 原件
├── docker-hub-research.md        ← 阶段 1: Docker Hub 研究数据
└── app-plan.md                   ← 阶段 2: 开发计划文档（用户批准）

apps/{app_name}/
├── .env                          ← 阶段 3: 环境变量
├── docker-compose.yml            ← 阶段 3: 编排文件
├── src/                          ← 阶段 3: 配置文件目录
│   ├── {config_files}
│   └── README.md
├── variables.json                ← 阶段 3: README 模板变量
├── CHANGELOG.md                  ← 阶段 3: 变更日志
├── Notes.md                      ← 阶段 3: 开发备注
└── README.md                     ← 阶段 4: 自动生成
```

---

## 阶段间数据传递

```
阶段 1 → 阶段 2:
  state.json.research_data (镜像信息、架构、官方 compose、W9_* 预判)

阶段 2 → 阶段 3:
  state.json.analysis_data.confirmed_decisions (用户批准的 W9_* 决策)
  app-plan.md (.env 预览、compose 预览、src/ 文件清单、改造说明)

阶段 3 → 阶段 4:
  state.json.development_data (生成的文件列表、验证结果)
  apps/{app_name}/ (实际应用文件)

阶段 4 → 完成:
  state.json.test_data (测试结果)
  apps/{app_name}/README.md (自动生成)
```

---

## 阶段文件引用

| 文件 | 路径 |
|------|------|
| 阶段 1: 研究 | `_bmad/bmb/workflows/app-curator/steps/step-01-research.md` |
| 阶段 2: 分析 | `_bmad/bmb/workflows/app-curator/steps/step-02-analysis.md` |
| 阶段 3: 开发 | `_bmad/bmb/workflows/app-curator/steps/step-03-development.md` |
| 阶段 4: 测试 | `_bmad/bmb/workflows/app-curator/steps/step-04-testing.md` |
| 计划模板 | `_bmad/bmb/workflows/app-curator/templates/app-plan-template.md` |
| 项目规范 | `_bmad-output/docker-library-spec.md` |
| 规范指南 | `.github/copilot-instructions.md` |

每个阶段文件包含：
- 流程概览（Phase 列表）
- 具体执行逻辑（Step 子步骤）
- 验证检查清单（每个 Phase 末尾）
- 用户确认点（Y/M/N 选择）
- 阶段切换逻辑（更新 state.json → 加载下一阶段文件）

---

## 用户确认点

整个工作流有 **3 个关键确认点**：

| 节点 | 位置 | 选项 | 说明 |
|------|------|------|------|
| 检查点 1 | 阶段 2 Phase 8 | Y/M/N | 批准开发计划 |
| 检查点 2 | 阶段 3 Phase 9 | Y/M/N | 确认生成文件 |
| 检查点 3 | 阶段 4 Phase 9 | Y/M/R/N | 确认测试通过，工作流完成 |

- **Y** = 批准，进入下一阶段
- **M** = 需要调整，修改后重新确认
- **R** = 重新测试（仅阶段 4）
- **N** = 暂停，保存状态稍后恢复

### 渐进式审批（复杂度驱动）

> 简单应用无需 3 次人工确认，可根据复杂度自动简化审批流程。

```
复杂度 ≤ 25 (简单应用, Pattern A/F):
  检查点 1: 自动审批 → agent 显示计划摘要但不等待，15秒后自动继续
  检查点 2: 自动审批 → agent 生成文件后直接进入测试
  检查点 3: 必须人工确认（保留）
  
  效果: 3 个确认 → 1 个确认，节省约 5-10 分钟等待

复杂度 26-50 (标准应用, Pattern B):
  检查点 1: 必须人工确认（W9_* 决策需要验证）
  检查点 2: 自动审批 → L1 通过后直接进入 L2
  检查点 3: 必须人工确认（保留）
  
  效果: 3 个确认 → 2 个确认

复杂度 > 50 (复杂应用, Pattern C/D/E):
  所有 3 个检查点均必须人工确认（保持不变）
```

**自动审批的安全保障：**
```
即使自动审批，agent 仍然:
  ✅ 输出完整的计划/文件摘要（用户可随时回滚）
  ✅ 执行所有 L1 检查（不跳过任何验证）
  ✅ 如果 L1 有 🔴 阻塞项 → 自动降级为人工确认
  ✅ state.json 记录 auto_approved=true（可追溯）
```

---

## 成功标准

✅ 从 Issue 到完整应用目录（含全部 7 个文件）  
✅ 所有配置符合 docker-library 规范  
✅ W9_* 决策有明确证据和用户确认  
✅ 自动化测试通过（容器启动 + HTTP 连通）  
✅ README.md 已自动生成  
✅ 环境已清理（无残留容器/卷）
