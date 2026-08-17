# 仓库自动化执行规范

| 属性 | 值 |
|------|-----|
| 状态 | 可实施草案 |
| 适用 | `docker-library` 仓库维护者、AI Worker、CI/CD 维护者 |
| 目标 | 统一仓库自动化执行边界、命令契约与门禁归属 |

---

## 1. 目的

本规范定义 `docker-library` 仓库中的自动化执行模型，明确以下问题：

1. 自动化能力如何分层
2. 哪些逻辑必须进入统一工具层
3. 哪些逻辑必须留在 CI/CD 编排层
4. CLI、Make、Workflow 的边界是什么
5. 质量门禁由谁执行、由谁阻断
6. 后续新增自动化脚本时应遵守什么契约

本规范是后续 DevOps 流程、CLI 设计、Make 设计、Workflow 重构的基础约束文档。

---

## 2. 适用范围

本规范覆盖以下仓库级自动化能力：

- app 生命周期操作
- 自动化校验与测试
- 派生文件生成
- 版本扫描
- 发布制品构建
- 外部元数据同步

本规范不覆盖以下内容：

- 云资源治理
- 线上运维值班
- 业务监控平台
- 消费端运行时逻辑
- Owner 最终 E2E 判断

---

## 3. 术语

### 3.1 核心逻辑层

指仓库内承载真实业务逻辑的代码层，例如：

- app 初始化
- app 归档
- metadata 读写
- README 生成
- compose 校验
- 部署验证
- 发布制品组装

### 3.2 统一 CLI 层

指将核心逻辑层暴露为稳定命令接口的工具层，面向：

- AI Worker
- CI/CD
- 本地脚本调用

### 3.3 Make 层

指面向人类终端使用者的快捷入口层，仅用于缩短命令和注入默认值。

### 3.4 CI/CD 编排层

指 GitHub Actions 等 workflow 层，负责：

- 触发时机
- 环境准备
- 密钥注入
- 产物上传
- 发布动作
- 阻断策略

### 3.5 质量门禁

指 `docs/ai-sdlc/05-quality-gates.md` 中定义的 Gate 0 至 Gate 4。

---

## 4. 核心原则

### 4.1 单一实现原则

同一自动化能力 MUST 只实现一次。

禁止以下情况：

- 在 CLI 中重新实现核心逻辑
- 在 Make 中复制逻辑
- 在 Workflow YAML 中重复实现校验规则

### 4.2 分层调用原则

允许的调用关系只有：

- 人类维护者 -> Make -> CLI -> 核心逻辑层
- AI Worker -> CLI -> 核心逻辑层
- CI/CD -> CLI -> 核心逻辑层

Workflow MAY 直接调用核心逻辑层中的单一脚本，但 SHOULD 优先通过统一 CLI 调用。

### 4.3 显式输入原则

自动化工具 MUST 优先使用显式参数，而不是隐式环境变量。

允许使用环境变量的场景：

- 密钥
- token
- CI 平台注入的上下文
- 可选默认值

禁止将普通业务输入长期隐藏在如下环境变量中：

- app 名称
- app 列表
- channel
- 输出目录
- 目标版本
- 归档原因

### 4.4 自动化与审批分离原则

自动化工具负责执行规则。
CI/CD 负责决定何时执行、在哪里执行、以及是否阻断。
Owner 负责最终 E2E 决策。

---

## 5. 分层模型

### 5.1 第 1 层：核心逻辑层

核心逻辑层 MUST 承载真实仓库动作。

包含但不限于：

- app 新建逻辑
- app 归档逻辑
- metadata 状态更新
- README 渲染
- `docker compose config` 校验
- `docker compose up -d` 验证
- reachability 检查
- 测试报告数据组装
- 发布制品构建
- Contentful 同步逻辑

核心逻辑层 MUST NOT：

- 解析复杂 CLI 子命令
- 依赖 Make
- 依赖 GitHub Actions 上下文
- 承担上传 R2、创建 Release、Cache Purge 等编排职责

### 5.2 第 2 层：统一 CLI 层

统一 CLI 层 MUST 提供稳定的命令面。

统一 CLI 层 SHOULD：

- 提供一致的参数风格
- 提供一致的退出码
- 支持人类可读输出
- 支持 `--json`
- 支持 `--dry-run`，适用于会修改文件或状态的命令
- 支持单 app 与多 app 的明确选择方式

统一 CLI 层 MUST NOT：

- 决定 workflow 触发时机
- 持有云上传逻辑
- 创建 GitHub Release
- 承担 Owner E2E
- 替代分支保护和审批流程

### 5.3 第 3 层：Make 层

Make 层 MAY 存在。
Make 层不是必需层。

如果存在，Make 层 MUST 仅承担：

- 快捷别名
- 参数缩写
- 常见默认值
- 多条 CLI 命令的轻量组合

Make 层 MUST NOT：

- 实现真实业务逻辑
- 成为 CI/CD 的唯一依赖
- 成为规范唯一入口

### 5.4 第 4 层：CI/CD 编排层

CI/CD 编排层 MUST 负责：

- 事件触发
- Runner 环境准备
- secret 注入
- 调用 CLI
- 收集日志和产物
- 上传制品
- 缓存清理
- 创建 Release
- 执行阻断策略

CI/CD 编排层 MUST NOT：

- 在 YAML 中实现复杂校验逻辑
- 在 YAML 中维护第二套版本判断规则
- 在 YAML 中复制 metadata 处理规则

### 5.5 第 5 层：流程与决策层

流程与决策层由以下文档定义：

- `docs/ai-sdlc/README.md`
- `docs/ai-sdlc/03-update-pipeline.md`
- `docs/ai-sdlc/04-new-app-pipeline.md`
- `docs/ai-sdlc/05-quality-gates.md`
- `docs/ai-sdlc/06-test-report-format.md`
- `docs/ai-sdlc/09-owner-e2e-runbook.md`

该层定义角色、流程、质量门禁与 Owner 责任。
自动化工具不得替代 Owner 的最终判断。

---

## 6. 命令契约

统一 CLI SHOULD 采用子命令结构。推荐结构如下：

```bash
library <group> <action> [options]
```

### 6.1 参数契约

统一 CLI MUST 遵守以下约定：

- 单 app 使用 `--app <name>`
- 多 app 使用 `--apps <a,b,c>` 或重复 `--app`
- 全量操作使用 `--all`
- 输出目录使用 `--output-dir`
- 通道使用 `--channel`
- 计划预演使用 `--dry-run`
- 机器可读输出使用 `--json`

### 6.2 退出码契约

统一 CLI SHOULD 使用一致退出码：

- `0`：成功
- `1`：业务失败或门禁失败
- `2`：参数错误
- `3`：外部依赖失败
- `4`：前置条件缺失
- `5`：内部异常

### 6.3 输出契约

统一 CLI MUST 输出简洁、可定位的问题信息。
当使用 `--json` 时，输出 MUST 稳定且适合 CI 与 AI 消费。

---

## 7. 标准命令组

以下命令组为推荐最小集合。

### 7.1 app 组

用于 app 生命周期操作。

推荐命令：

```bash
library app new --app <name>
library app archive --app <name>
library app info --app <name>
library app list
```

职责：

- 新建 app 骨架
- 归档 app
- 查询 app 状态
- 枚举 app 集合

### 7.2 validate 组

用于 Gate 0 至 Gate 3 的自动化门禁。

推荐命令：

```bash
library validate --app <name>
library validate structure --app <name>
library validate policy --app <name>
library validate deploy --app <name>
library validate reachability --app <name>
```

职责：

- 结构校验
- 策略校验
- compose 校验与部署验证
- 可访问性与日志验证

### 7.3 test 与 report 组

用于自动化验证与报告生成。

推荐命令：

```bash
library test --app <name>
library report --app <name>
```

职责：

- 执行动静态验证集合
- 按 `docs/ai-sdlc/06-test-report-format.md` 生成结果

### 7.4 docs 组

用于派生文档与派生文件生成。

推荐命令：

```bash
library docs readme --app <name>
library docs readme --all
```

职责：

- 生成或刷新 README
- 后续 MAY 扩展到其他派生文件

### 7.5 versions 组

用于版本扫描和维护计划输入。

推荐命令：

```bash
library versions scan --selection due
library versions scan --selection all-active
```

职责：

- 检测上游版本候选
- 生成更新输入
- 为 issue 或 work queue 提供依据

### 7.6 publish 组

用于构建发布制品，不负责上传和发布审批。

推荐命令：

```bash
library publish build --channel dev
library publish build --channel rc
library publish build --channel release
```

职责：

- 组装制品
- 执行本地制品级校验
- 生成 manifest、checksum、archive

### 7.7 contentful 组

用于外部元数据同步。

推荐命令：

```bash
library contentful sync --app <name>
library contentful sync --apps <a,b>
```

职责：

- 将仓库中的 app metadata 同步到 Contentful
- 处理归档场景下的 `production=false` 等状态

---

## 8. 质量门禁归属

质量门禁归属 MUST 与 `docs/ai-sdlc/05-quality-gates.md` 保持一致。

| Gate | 内容 | 执行者 | 阻断者 |
|------|------|--------|--------|
| Gate 0 | 结构校验 | CLI / AI / CI | CI |
| Gate 1 | 策略校验 | CLI / AI / CI | CI |
| Gate 2 | 部署校验 | CLI / AI / CI | CI |
| Gate 3 | AI 验证与报告 | CLI / AI | CI 或任务流程 |
| Gate 4 | Owner E2E | Owner | Owner |

约束如下：

- Gate 0 至 Gate 3 的检查逻辑 MUST 可由 CLI 执行
- Gate 4 MUST 保持人工判断
- CI MUST 使用 CLI 返回结果进行阻断
- Owner SHOULD 不重复 AI 已完成的例行检查

---

## 9. Make 的定位

Make 在本仓库中是可选层，不是核心层。

原因如下：

- 本仓库为 AI-first SDLC
- AI 与 CI 更需要稳定 CLI，而不是 Make
- Make 更适合人类本地便捷操作

如果提供 Make，推荐仅保留轻量目标：

```make
make check APP=wordpress
make test APP=wordpress
make readme APP=wordpress
make publish CHANNEL=dev
```

Make SHOULD 仅转发到 CLI。
Make MUST NOT 成为真实逻辑的实现位置。

---

## 10. CI/CD 的定位

CI/CD 的职责是编排，不是业务规则实现。

CI/CD MUST 负责：

- 触发条件
- 运行环境准备
- 凭证注入
- 调用 CLI
- 上传制品
- 发布 release
- 执行阻断和通知

CI/CD SHOULD NOT 负责：

- metadata 规则解析
- app 归档规则实现
- README 生成逻辑实现
- 版本判断核心逻辑实现
- 门禁规则重复实现

换言之：

- CLI 负责“怎么检查、怎么构建、怎么变更”
- CI/CD 负责“什么时候跑、在哪跑、跑完之后做什么”

---

## 11. 非目标

本规范明确以下内容不属于统一 CLI 的核心职责：

- GitHub PR 创建
- GitHub Issue 创建
- Merge Policy
- Branch Protection
- Cache Purge 决策
- Release 审批
- Owner E2E 决策
- 消费端数据消费逻辑

这些能力 MAY 由 workflow、平台或人工流程承担。

---

## 12. 兼容与演进规则

后续新增自动化能力时 MUST 先回答三个问题：

1. 这是核心逻辑、CLI、Make 还是 Workflow 职责
2. 该能力是否会被 AI、CI、本地重复调用
3. 该能力是否应进入统一命令契约

判断规则：

- 若是可重复仓库动作，SHOULD 进入核心逻辑层
- 若要被 AI 或 CI 调用，SHOULD 暴露为 CLI
- 若只是人类快捷入口，MAY 提供 Make
- 若依赖 secret、上传、审批、平台事件，SHOULD 留在 CI/CD

---

## 13. 落地顺序

推荐按以下顺序实施：

1. 先统一现有 `build/*.py` 的输入输出契约
2. 再抽出统一 CLI
3. 再让 workflow 优先调用 CLI
4. 最后按需补 Make 别名

推荐优先落地的命令组：

1. `validate`
2. `test`
3. `report`
4. `app archive`
5. `docs readme`
6. `versions scan`
7. `publish build`

---

## 14. 与现有文档的关系

本规范不替代以下文档：

- `docs/architecture.md`
- `docs/ai-sdlc/*.md`
- `docs/appstore-release-spec.md`

关系如下：

- `architecture.md` 定义仓库结构
- `ai-sdlc` 定义流程、角色、门禁
- `appstore-release-spec.md` 定义发布产物模型
- 本规范定义自动化执行边界和命令契约

---

## 15. 一句话结论

本仓库的自动化能力 SHOULD 以“核心逻辑层 + 统一 CLI”为中心构建。
Make 是可选的人类快捷入口。
CI/CD 是编排层，不是逻辑层。
Owner E2E 保持人工最终裁决。
