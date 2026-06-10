# Appstore 发布规范

| 属性 | 值 |
|------|-----|
| 状态 | 可实施草案 |
| 适用 | docker-library 仓库维护者、发布负责人、消费端开发者 |

---

## 1. 核心模型

`appstore` 是本项目的发布目标——一个由两个子数据集组成的聚合制品：

| 子数据集 | 内容 | 事实源 |
|----------|------|--------|
| **catalog** | 应用描述（名称、分类、简介、截图 URL、logo URL 等） | Contentful |
| **library** | 安装模板（`variables.json`、`.env`、`docker-compose.yml` 等） | 本仓库 `apps/` 目录 |

**appstore 不是第三套独立事实源**——它是对 catalog 与 library 的聚合与发布。

### 职责边界

| 本项目负责 | 本项目不负责 |
|-----------|-------------|
| 维护 `apps/` 下的安装模板 | 提供 appstore 在线 API |
| 从 Contentful 拉取 catalog 数据 | 决定下游（AppOS、Console）如何消费 |
| 组装并发布完整的 `appstore` 制品到 R2 | 将消费端逻辑耦合进发布规范 |
| 并行期内同时维护 legacy 与 v2 | — |

---

## 2. 版本语义

发布体系中区分三类版本，分别作用于 `catalog`、`library` 和 `appstore` 根级：

| 版本 | 含义 | 变更条件 | 格式 |
|------|------|---------|------|
| `schemaVersion` | 数据结构契约版本 | 删字段、改类型、改文件布局 | 单调递增字符串（`"1"`, `"2"`） |
| `datasetVersion` | 数据内容快照版本 | **任何**内容变更 | 内容哈希（SHA-256 前 16 位 hex） |
| `channel` | 稳定性通道 | 发布目标决定 | `dev` / `rc` / `release` |

`catalog`、`library` 和 `appstore` 根级各自拥有**独立**的 `datasetVersion`：

- `catalog.datasetVersion`：基于 4 个 catalog JSON 文件的校验和计算
- `library.datasetVersion`：基于 `apps-index` 的序列化内容计算
- `appstore.datasetVersion`：基于上述两者的组合计算

这意味着**纯 catalog 描述变更不会导致 `library.datasetVersion` 变化**（反之亦然），客户端可精确判断哪部分数据需要刷新。

### 2.1 schemaVersion 兼容性承诺

同一 `schemaVersion` 内遵循**"只增不减"**规则：

- ✅ 可以：新增字段、新增文件、新增 app 条目
- ❌ 不能：删除已有字段、改变字段类型、改变文件命名规则
- 消费者忽略未知字段后仍能正常工作

**这意味着 99% 的日常变更只触发 `datasetVersion` 递增，不触发 `schemaVersion` 升级。**

### 2.2 schemaVersion 升级条件

以下任一发生时才升级：
- 删除已有字段
- 改变字段类型
- 改变文件布局或 manifest 自身结构

升级流程：提前公告 → 过渡期新旧并存 → 消费者升级 → 下线旧格式。

### 2.3 消费者兼容性

消费者维护自己支持的 `schemaVersion` 列表，下载 manifest 后自行判断：

```
if manifest.schemaVersion in SUPPORTED:
    正常消费
else:
    回退到上次成功的 datasetVersion 快照，提示用户升级
```

此模式对标 Helm（`apiVersion`）、Docker Registry（`schemaVersion`）、OSTree（`summary.version`）的行业惯例。

---

## 3. 更新粒度

| 数据集 | 粒度 | 说明 |
|--------|------|------|
| **catalog** | 全量文件 | 任一 JSON 变化 → 新快照；无字段级 delta |
| **library** | app 级 | 以 `apps/<app>` 为判断单元；变更类型：`addedApps` / `changedApps` / `removedApps` |

`apps-delta` 只表达**变更范围**，真正的增量载荷由单 app 制品承担。客户端更新策略：

1. 首装或本地损坏 → 下载全量包
2. 增量更新 → 仅下载 `addedApps` + `changedApps` 对应的 app 包
3. `removedApps` → 本地删除
4. 任一 app 更新失败 → 回退到全量包恢复

---

## 4. 输出物模型

### 4.1 R2 目录结构

```
artifact/appstore/<channel>/
├── catalog/
│   ├── manifest.json
│   ├── full/
│   │   └── catalog-<datasetVersion>.zip
│   ├── catalog_en.json
│   ├── catalog_zh.json
│   ├── product_en.json
│   ├── product_zh.json
│   └── *.sha256
├── library/
│   ├── manifest.json
│   ├── apps-index-<datasetVersion>.json
│   ├── apps-delta-<fromVersion>-to-<toVersion>.json
│   ├── full/
│   │   ├── library-<datasetVersion>.zip
│   │   └── library-<channel>.zip
│   └── apps/
│       └── <app>/
│           ├── latest.zip
│           └── latest.zip.sha256
└── manifests/
    └── appstore-manifest.json
```

### 4.2 设计要点

| 要点 | 说明 |
|------|------|
| 全量包兜底 | 每次发布都重建，用于首装、灾备、回退 |
| 单 app 包仅 `latest.zip` | 不保留版本化包，R2 仅作分发缓存；审计追溯由 git 保证 |
| 增量构建 | 仅 `addedApps` + `changedApps` 触发重建，未变更 app 不触碰 |
| 上传策略 | `aws s3 sync`（默认不删除），首次发布由 `check_seed` 检测并全量播种 |
| 无孤儿堆积 | 单 app 只有 2 个文件，无需定时清理 |
| 图片 | v2 使用在线 URL，不打包二进制 |

---

## 5. Manifest 契约

### 5.1 appstore 根 manifest

```json
{
  "schemaVersion": "1",
  "datasetVersion": "2dccc0f5e5f0d21f",
  "channel": "release",
  "catalog": {
    "manifest": "catalog/manifest.json",
    "datasetVersion": "7ee7a10b7da49f38"
  },
  "library": {
    "manifest": "library/manifest.json",
    "datasetVersion": "85f687824c03ef93"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

消费者只需下载这一个文件，即可通过 `catalog.datasetVersion` 和 `library.datasetVersion` 分别判断哪部分数据需要更新。

### 5.2 catalog manifest

```json
{
  "schemaVersion": "1",
  "datasetVersion": "7ee7a10b7da49f38",
  "source": "contentful",
  "fullPackage": "full/catalog-2026.06.09.120000.zip",
  "files": {
    "catalogEn": "catalog_en.json",
    "catalogZh": "catalog_zh.json",
    "productEn": "product_en.json",
    "productZh": "product_zh.json"
  },
  "checksum": {
    "catalogEn": "catalog_en.json.sha256",
    "catalogZh": "catalog_zh.json.sha256",
    "productEn": "product_en.json.sha256",
    "productZh": "product_zh.json.sha256",
    "fullPackage": "full/catalog-2026.06.09.120000.zip.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 5.3 library manifest

```json
{
  "schemaVersion": "1",
  "datasetVersion": "85f687824c03ef93",
  "channel": "release",
  "fullPackage": {
    "versioned": "full/library-2026.06.09.120000.zip",
    "latest": "full/library-release.zip"
  },
  "appsIndex": "apps-index-85f687824c03ef93.json",
  "appsDelta": "apps-delta-7ee7a10b7da49f38-to-85f687824c03ef93.json",
  "appPackagesBase": "apps/",
  "supportsPartialUpdate": true,
  "checksum": {
    "fullPackageVersioned": "full/library-2026.06.09.120000.zip.sha256",
    "fullPackageLatest": "full/library-release.zip.sha256",
    "appsIndex": "apps-index-85f687824c03ef93.json.sha256",
    "appsDelta": "apps-delta-7ee7a10b7da49f38-to-85f687824c03ef93.json.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 5.4 apps-index 条目结构

```json
{
  "app": "nginx",
  "name": "Nginx",
  "hash": "d80b08f74959...",
  "versions": ["1.26", "latest"],
  "path": "apps/nginx",
  "package": { "latest": "apps/nginx/latest.zip" },
  "checksum": { "latest": "apps/nginx/latest.zip.sha256" }
}
```

客户端通过对比 `hash` 字段判断 app 是否变更。

---

## 6. 发布流程

### 6.1 触发方式

| 事件 | channel |
|------|---------|
| push 到 `dev` 分支 | `dev` |
| push 到 `main` 分支 | `release` |
| `workflow_dispatch` | 手动选择 `dev` / `rc` / `release` |

### 6.2 CI 流水线（`appstore-publish.yml`）

```
1. 检出代码（fetch-depth: 0）
2. 解析 channel
3. 检查 R2 apps/ 是否为空 → 空则标记首次发布（--all-apps）
4. 从 Contentful 拉取 catalog 源数据
5. 运行 library_publish.py 构建所有制品（v2 + legacy）
6. 上传 v2 制品到新 R2 路径
7. 上传 legacy 制品到旧 R2 路径（兼容旧消费者）
8. 清除 Cloudflare 缓存
9. release 通道额外创建 GitHub Release
```

### 6.3 上传策略

| 目标 | 命令 | R2 路径 |
|------|------|--------|
| v2 catalog | `aws s3 sync` | `appstore/<channel>/catalog/` |
| v2 library 元数据 | `aws s3 sync --exclude "apps/*"` | `appstore/<channel>/library/` |
| v2 单 app 包 | `aws s3 cp --recursive` | `appstore/<channel>/library/apps/` |
| v2 manifests | `aws s3 sync` | `appstore/<channel>/manifests/` |
| legacy library | `aws s3 sync` | `<channel>/websoft9/plugin/library/` |
| legacy media | `aws s3 sync` | `<channel>/websoft9/plugin/media/` |

所有 `sync` 均为默认追加/覆盖模式，不删除目标已有文件。

---

## 7. Legacy 兼容

并行期内 legacy 与 v2 通过**同一 workflow、不同 R2 路径**共存：

| 制品 | v2 路径 | legacy 路径 |
|------|--------|------------|
| catalog | `appstore/<channel>/catalog/` | `<channel>/websoft9/plugin/media/`（打包为 `media.zip`） |
| library | `appstore/<channel>/library/` | `<channel>/websoft9/plugin/library/`（打包为 `library-*.zip`） |

**legacy `media.zip` 保持旧格式**：内含 `json/` + `logos/` + `screenshots/`，图片从 Contentful URL 下载后打包。v2 目录中不包含图片二进制，统一使用在线 URL。

每次 push 同时产出两套制品，迁移窗口结束后下线 legacy 上传步骤。

---

## 8. 校验门禁

发布时必须通过以下检查，任一失败则中止：

1. catalog 四个核心 JSON 可生成
2. catalog / library / appstore 三层 manifest 字段完整、可追溯
3. `apps-index` 和 `apps-delta` 可生成，delta 结构符合 app 级定义
4. 所有 checksum 与实际文件一致
5. 单 app 制品可生成（每个变更 app 的 `latest.zip` + `.sha256`）
6. 根 manifest 可追溯到 catalog 与 library
7. Legacy 兼容制品完整性

---

## 9. Phase 1 范围

| # | 事项 |
|---|------|
| 1 | 保留 legacy workflow，新增独立 v2 workflow |
| 2 | 新增 `v2/<channel>/appstore/{catalog,library,manifests}` 目录结构 |
| 3 | 为三层分别建立 `schemaVersion` + `datasetVersion` |
| 4 | 旧 library / catalog 构建逻辑迁回本项目 |
| 5 | Library 更新粒度固定为 app 级 |
| 6 | 全量包 + 单 app 包（`latest.zip`）双输出 |
| 7 | Manifest + checksum 覆盖所有制品 |
| 8 | 首次发布自动全量播种，后续增量构建 |

---

## 10. 行业对标

本规范对标 **Static Artifact Repository** 模式（Helm Chart Repo、OSTree Summary、APT Repo）：

| 特性 | 对标 | 本规范 |
|------|------|--------|
| 索引发现 | Helm `index.yaml` | `apps-index-{dsv}.json` |
| 增量更新 | OSTree static-deltas | `apps-delta-{from}-to-{to}.json` |
| 校验链 | APT `Release` + SHA-256 | `*.sha256` 贯穿三层 manifest |
| 通道隔离 | Debian stable/testing | `dev` / `rc` / `release` |
| 制品签名 | Phase 2 | 计划中 |

> **Phase 2 展望**：制品签名（对标 TUF/Helm provenance）、SLSA 出处证明。

---

## 11. 消费者指南

消费者无需维护额外的状态文件——**上一次下载成功的 `appstore-manifest.json` 本身就是完整的状态记录**。更新时将新下载的 manifest 与本地缓存的旧 manifest 对比即可。

### 11.1 首次安装（冷启动）

```
1. 下载 appstore-manifest.json
2. 检查 schemaVersion 兼容性 → 不兼容则中止

3. 下载 catalog 全量数据：
   → 下载 catalog/manifest.json
   → 下载 catalog-<datasetVersion>.zip（全量包，1 次请求 1 次校验）
   → 校验 catalog-<datasetVersion>.zip.sha256
   → 解压到本地

4. 下载 library 全量数据：
   → 下载 full/library-<channel>.zip（全量包，含所有 app 模板）
   → 校验 full/library-<channel>.zip.sha256
   → 解压到本地 apps/ 目录

5. 保存本次下载的 appstore-manifest.json 到本地作为状态锚点
```

### 11.2 增量更新

```
1. 下载最新的 appstore-manifest.json

2. 对比新 manifest 与本地缓存的旧 manifest：
   → 如果 catalog.datasetVersion 不同：
       下载 catalog/manifest.json → 逐个对比 checksum → 下载变更的 JSON
   → 如果 library.datasetVersion 不同：
       if supportsPartialUpdate:
         下载 apps-delta → 下载 changed/added app 的 latest.zip
       else:
         下载全量包
   → 如果都相同：什么都不做，结束

3. 更新成功后，用新 manifest 替换本地缓存
```

**典型场景开销**：

| 场景 | HTTP 请求 |
|------|----------|
| 无变化 | 1（appstore-manifest.json，~200B） |
| 仅 catalog 变了 1 个文件 | 3（根 manifest + catalog manifest + 1 个 JSON） |
| 仅 library 变了 2 个 app | 4（根 manifest + library manifest + delta + 2 个 zip） |

### 11.3 异常恢复

```
增量更新中任一文件下载或校验失败：
  → 回退策略：下载 full/library-<channel>.zip 全量覆盖本地 apps/
  → 用本次下载的 manifest 替换本地缓存

schemaVersion 不在本地支持列表中：
  → 不更新任何数据，保持本地缓存的旧 manifest
  → 提示用户升级客户端
  → 提示用户升级客户端
```

### 11.4 缓存策略建议

| 资源 | 建议 | 原因 |
|------|------|------|
| `appstore-manifest.json` | Cache-Control: 60s | 入口文件，需及时感知更新 |
| `catalog/manifest.json` | Cache-Control: 60s | 体积极小，变更频率低 |
| `apps-delta-*.json` | Cache-Control: 60s | 体积极小 |
| `apps/{app}/latest.zip` | Cache-Control: 60s | 模板文件体积极小，变更后需立即生效 |
| `full/library-{dsv}.zip` | immutable | 文件名含内容版本，永不变 |
| `*.sha256` | 跟随对应文件 | 校验与被校验文件同步缓存 |
| `catalog_*.json / product_*.json` | Cache-Control: 3600 | 描述数据，变更频率中等 |
