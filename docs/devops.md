# Docker Library 发布治理规范

创建时间：2026-06-08
更新时间：2026-06-09
状态：可实施草案
适用对象：docker-library 仓库维护者、发布负责人、DevOps

## 1. 文档目的

本文档定义当前项目在 appstore v2 发布模型中的职责、输入、输出、目录结构、版本语义与发布门禁。

它回答六件事：

1. 当前项目在 appstore 制品体系中的角色是什么
2. appstore 大制品由哪些子数据集组成
3. catalog 与 library 分别来自哪里
4. 当前项目应该如何组装并发布 appstore 制品
5. 并行期内 legacy 与 v2 应如何共存
6. 发布时如何表达版本、快照与兼容性

## 2. 核心模型

当前项目不再只发布 `library` 单一数据集，而是负责组装并发布 `appstore` 这个大制品。

`appstore` 由两个并列子数据集组成：

1. `catalog`
2. `library`

其中：

1. `catalog` 表达应用描述信息，例如名称、分类、标题、简介、截图 URL、logo URL、推荐位等
2. `library` 表达安装模板信息，例如 `variables.json`、`.env`、`docker-compose.yml`、模板文件和安装相关索引
3. `appstore` 是对外发布的聚合制品，不是第三套独立事实源

结论：当前项目的发布目标不是单独发布 `library`，而是组装并发布包含 `catalog` 与 `library` 的 `appstore` 聚合制品。

## 3. 职责边界

当前项目在第一阶段承担以下职责：

1. 维护 `library` 所需的安装真相数据
2. 拉取或接收 `catalog` 所需的描述数据输入
3. 生成 `catalog` 子数据集
4. 生成 `library` 子数据集
5. 生成 `appstore` 根级 manifest
6. 把完整 `appstore` 制品发布到 R2
7. 在并行期内同时维护 legacy 与 v2 两条发布边界

当前项目不负责：

1. 提供 appstore 在线 API
2. 决定 Appos、Websoft9、Console 等下游如何消费
3. 将消费端逻辑反向耦合进发布规范

补充说明：

1. `catalog` 的事实源仍然是 Contentful
2. `websoft9` 仓库中历史的 `media.yml` 仅是旧的构建与分发链路，不再应被视为事实源
3. 当前项目现在承担 appstore 聚合构建职责，因此文档必须同时描述 `catalog` 与 `library`
4. 当前项目还需要接管旧 library 与旧 catalog 兼容制品的实际构建逻辑
5. 新版 `appstore v2` 不再打包图片二进制资源，而是直接使用在线图片 URL

## 4. 旧机制盘点

在进入新设计之前，必须先明确当前 legacy 机制并不是单一链路，而是至少包含以下几类逻辑：

### 4.1 旧 library dev 链路

特征如下：

1. 在当前仓库构建 `library-dev.zip`
2. 发布到 legacy R2 路径
3. 末尾触发外部仓库的 `media_dev.yml`

风险在于：

1. 当前仓库只掌握了 library 的一部分发布逻辑
2. catalog 兼容制品依赖外部 workflow 是否还存在
3. 一旦外部 workflow 名称、ref 或触发方式变化，旧链路就会失效

### 4.2 旧 library release 链路

特征如下：

1. 在当前仓库构建 release library 制品
2. 从外部 `websoft9` 仓库 Dockerfile 反向推导版本和通道
3. 发布到 legacy R2 路径
4. 触发外部文档仓库 workflow

风险在于：

1. 当前仓库没有完整发布主权
2. 版本和通道判断依赖外部仓库状态
3. 下游编排依赖外部 workflow 是否稳定存在

### 4.3 旧 catalog release 链路

特征如下：

1. 真实事实源是 Contentful
2. 旧 `websoft9` 仓库中的 `media.yml` 负责拉取 catalog 与 product 数据
3. 同时拉取 logo、screenshot 等资源
4. 最终生成 legacy catalog 或 media 兼容制品

结论：旧 catalog release 的事实源不是 `websoft9` 仓库，而是 Contentful；`websoft9` 只是旧编排器。上述图片资源打包方式仅属于 legacy 兼容逻辑，不属于 v2 标准输出。

### 4.4 旧 catalog dev 链路

特征如下：

1. 真实事实源仍然是 Contentful
2. 旧 `media_dev.yml` 会下载 `library-dev.zip`
3. 再把 library 中的版本信息合并进 product 数据
4. 最终生成 dev 兼容 catalog 或 media 制品

结论：旧 catalog dev 不是纯 catalog 输出，而是“Contentful 描述数据 + library 版本数据”的兼容拼装结果。

### 4.5 旧机制的核心问题

旧机制真正需要替换的不是旧制品本身，而是旧的跨仓库 workflow 依赖。

问题主要包括：

1. 当前仓库对 legacy 产物没有完整发布主权
2. 关键发布步骤散落在外部仓库 workflow 中
3. 外部项目升级 workflow 后，当前仓库可能无法继续触发旧流程
4. catalog 迁回当前项目后，再继续依赖外部 workflow 会让职责边界更加混乱

## 5. 输入真相面

`appstore` 的输入真相面分为双源。

### 4.1 catalog 输入真相面

来源：Contentful

第一阶段最小发布集合包括：

1. `catalog_en.json`
2. `catalog_zh.json`
3. `product_en.json`
4. `product_zh.json`

说明：

1. 上述四个 JSON 表达 appstore 描述数据的当前最小发布集合
2. 第一阶段允许沿用既有四文件形态，以兼容历史消费侧
3. 但第一阶段不能把 `catalog` 简化为“只有四个 JSON 文件”，而必须把它视为有正式契约版本的独立数据集
4. 后续如需重构 catalog 结构，应通过提升 `catalog.schemaVersion` 进行，而不是在无版本边界的情况下直接改写
5. `appstore v2` 中的图片字段应以在线 URL 表达，不再要求打包图片二进制文件

### 4.2 library 输入真相面

来源：当前仓库自身

最小输入包括：

1. `apps/<app>/variables.json`
2. `apps/<app>/.env`
3. `apps/<app>/docker-compose.yml` 或等效模板
4. `apps/<app>` 下其他安装所需文件

要求：

1. 发布时不从其他仓库反向推导安装真相
2. `apps/<app>` 是 `library` 更新判断的基本单元
3. 第一阶段不定义 `apps/<app>` 内部文件级更新语义
4. 第一阶段不能把 `library` 简化为“只有压缩包和索引文件”，而必须把它视为有正式契约版本的独立数据集

## 6. 并行期发布策略

第一阶段不是一次性切断 legacy，而是进入一段并行运行期。

并行期采用“双链路、双目录、双消费面”策略：

1. legacy 继续按现有方式发布并运行一段时间
2. `appstore v2` 通过新的独立 workflow 发布
3. legacy 与 v2 使用彼此独立的 R2 目录
4. legacy 与 v2 的消费者在并行期内分别按各自契约消费
5. 在明确完成迁移窗口之前，不以 v2 覆盖 legacy

并行期设计要求如下：

1. legacy workflow 可以继续存在并继续执行
2. v2 workflow 必须独立，不依赖 legacy workflow 的结果物
3. v2 R2 路径必须独立，不覆盖 legacy 路径
4. legacy 的稳定性与故障不应阻断 v2 发布
5. v2 的结构演进也不应反向污染 legacy 契约
6. legacy 兼容制品可以继续保留，但旧的跨仓库编排依赖必须逐步迁回当前项目

结论：第一阶段应采用独立的新 workflow 和独立的新 R2 目录，同时允许 legacy 继续运行一段时间。

## 7. 发布设计原则

当前项目采用“一个核心发布域 + 多个兼容入口”的设计，而不是完全分裂成两套独立系统。

### 7.1 设计原则

1. 旧制品优先稳定，不轻易改变旧路径、旧命名和旧消费面
2. 旧 workflow 文件可以保留，但其内部真实构建逻辑必须迁回当前项目
3. v2 制品通过新的标准路径独立发布
4. 当前项目必须成为 legacy 与 v2 的唯一发布编排方

### 7.2 入口层设计

第一阶段允许同时存在三类入口：

1. legacy dev 入口
2. legacy release 入口
3. v2 主入口

这些入口的职责应尽量薄化，只负责：

1. 确定 channel
2. 传递兼容模式参数
3. 调用当前项目内的核心发布流程

### 7.3 核心发布域

核心发布域负责统一编排以下几类输出：

1. legacy library 输出
2. legacy catalog 输出
3. v2 catalog 输出
4. v2 library 输出
5. appstore 根级 manifest 输出

### 7.4 为什么不继续依赖外部 workflow

不再把外部 workflow 作为主发布链必要步骤，原因如下：

1. 外部 workflow 名称、分支、触发方式会变化
2. 当前项目需要对 legacy 兼容产物拥有可控的发布能力
3. catalog 已迁回当前项目职责范围后，继续依赖外部 workflow 会放大耦合
4. 主发布链必须由当前项目完全控制

结论：应保留旧入口，不保留旧的外部 workflow 依赖。

## 8. 输出物模型

第一阶段每次发布同时产出三层 v2 输出，并允许 legacy 输出继续存在。

### 6.1 appstore 根级输出

至少包含：

1. `appstore-manifest.json`
2. `appstore-manifest.json.sha256`

### 6.2 catalog 输出

至少包含：

1. `manifest.json`
2. `catalog_en.json`
3. `catalog_zh.json`
4. `product_en.json`
5. `product_zh.json`
6. 上述文件对应 checksum

### 6.3 library 输出

至少包含：

1. `manifest.json`
2. `apps-index-<datasetVersion>.json`
3. `apps-delta-<fromVersion>-to-<toVersion>.json`
4. `library` 全量主制品
5. `apps/<app>` 级独立制品集合
6. 上述文件对应 checksum

补充要求：

1. `library` 必须同时保留全量包与单 app 包两类输出
2. 全量包用于首装、回退、灾备与旧客户端兼容
3. 单 app 包用于新增 app 和变更 app 的网络增量分发
4. 第一阶段单 app 制品粒度固定到 `apps/<app>`，不继续细化到 app 内文件级制品
5. 单 app 制品应同时提供可覆盖的最新别名与不可变的版本化对象

### 6.4 legacy 输出

并行期内必须保留：

1. `library-dev.zip`
2. `library-latest.zip` 或既有正式包命名
3. 上述旧制品的既有兼容发布方式

### 8.4 legacy catalog 输出

并行期内也必须保留旧 catalog 或 media 兼容制品。

第一阶段要求：

1. 旧 catalog 兼容输出仍可被旧消费者继续使用
2. 旧 catalog dev 兼容逻辑继续保留“描述数据 + library 版本数据”的拼装语义
3. 但该拼装逻辑必须迁回当前项目内部实现，不再通过外部 workflow 串联

### 8.5 v2 catalog 输出约束

`appstore v2` 的 `catalog` 输出不再打包图片二进制资源。

要求如下：

1. `catalog` 中的 logo、screenshot 等字段统一使用在线 URL
2. v2 路径下不再要求提供 `logos/`、`screenshots/` 或等价图片目录
3. legacy 如仍需要图片打包，可作为兼容输出单独保留，但不得反向污染 v2 结构

## 9. workflow 约束

第一阶段不要求用一个 workflow 同时承载 legacy 与 v2。

推荐采用两类 workflow：

1. legacy workflow
2. `appstore v2` workflow

其中：

1. legacy workflow 继续服务旧目录和旧消费者
2. `appstore v2` workflow 只负责新的 `appstore` 制品
3. 两者在并行期内独立运行
4. legacy workflow 可以作为兼容入口保留，但其内部逻辑应调用当前项目内的核心发布实现

新的 v2 workflow 应采用中性命名，不强绑定消费端产品名称。

推荐名称可为：`appstore-publish.yml`，或保持现有中性命名，但其职责必须明确是发布完整 `appstore v2`。

v2 workflow 的职责应为：

1. 接收 `channel=dev|rc|release`
2. 组装同一通道下的 `catalog` 与 `library`
3. 生成 `appstore` 根级 manifest
4. 只写入 v2 路径
5. 发布决策只由当前项目完成，不依赖其他业务仓库决定版本和通道

要求：

1. legacy 与 v2 可以并行，但边界必须清晰
2. `dev`、`rc`、`release` 只表达稳定性通道，不表达契约版本
3. 当前主流程以 `dev` 和 `release` 为主
4. `rc` 作为预留候选发布通道，仅在需要时手动触发
5. v2 workflow 不应依赖 legacy workflow 的产物或状态
6. legacy workflow 不应承担 v2 聚合职责
7. legacy workflow 不应再依赖外部仓库 workflow 是否存在
8. legacy workflow 与 v2 workflow 都应复用当前项目内部的核心构建逻辑

推荐触发方式：

1. `dev` 分支 push 自动发布 `dev`
2. `main` 分支 push 自动发布 `release`
3. `rc` 保留手动预发布入口

## 10. R2 目录结构

第一阶段的 v2 目录结构应升级为：

1. `artifact/websoft9/v2/dev/appstore/`
2. `artifact/websoft9/v2/rc/appstore/`
3. `artifact/websoft9/v2/release/appstore/`

每个通道下的目录结构保持一致：

1. `catalog/`
2. `library/`
3. `manifests/`

建议结构如下：

1. `artifact/websoft9/v2/<channel>/appstore/catalog/`
2. `artifact/websoft9/v2/<channel>/appstore/library/`
3. `artifact/websoft9/v2/<channel>/appstore/manifests/`

要求：

1. 新路径是新增，不替代旧路径
2. 旧路径继续存在并继续服务 legacy 运行时
3. v2 路径与 legacy 路径必须物理隔离
4. `appstore` 根级所有子数据集都必须能通过根 manifest 追溯
5. `catalog` 与 `library` 都必须有各自 manifest

### 10.1 library 子目录建议结构

为支持真正的 app 级增量分发，`library/` 下建议采用以下结构：

1. `artifact/websoft9/v2/<channel>/appstore/library/manifest.json`
2. `artifact/websoft9/v2/<channel>/appstore/library/apps-index-<datasetVersion>.json`
3. `artifact/websoft9/v2/<channel>/appstore/library/apps-delta-<fromVersion>-to-<toVersion>.json`
4. `artifact/websoft9/v2/<channel>/appstore/library/full/library-<datasetVersion>.zip`
5. `artifact/websoft9/v2/<channel>/appstore/library/full/library-<channel>.zip`
6. `artifact/websoft9/v2/<channel>/appstore/library/apps/<app>/latest.zip`
7. `artifact/websoft9/v2/<channel>/appstore/library/apps/<app>/latest.zip.sha256`

说明：

1. `full/library-<datasetVersion>.zip` 是不可变的全量快照包，`<datasetVersion>` 使用全局发布时间戳
2. `full/library-<channel>.zip` 是该通道下的全量最新别名，可被覆盖
3. `apps/<app>/latest.zip` 是该 app 在该通道下的唯一安装包，每次 app 内容变更时覆盖更新
4. R2 上的历史审计与回滚能力由 git 仓库保证，R2 仅作为分发缓存
5. 客户端通过 `apps-index` 中的 `hash` 字段判断 app 是否变更，无需版本化文件名

### 10.2 单 App 包构建优化

每个 app 只保留一个 `latest.zip`，构建流程采用按需覆盖策略：

1. **首次发布**（R2 上 `apps/` 为空）：为所有 app 构建 `latest.zip`（全量冷启动）
2. **增量发布**（R2 已播种）：**仅**为 `apps-delta` 中的 `addedApps` 与 `changedApps` 构建/覆盖 `latest.zip`
3. 未变更 app 的 `latest.zip` 不重新构建、不触碰——R2 上已有文件保持不变

此优化依赖 R2 上传步骤采用 `aws s3 sync` 默认行为（追加/覆盖，不删除），配合 `check_seed` 步骤检测首次发布。

优化效果（以 300 个 app、每次变更 2 个为例）：

| 指标 | 全量构建 | 增量构建 |
|------|---------|---------|
| 单 app zip 打包次数 | 300 | 2 |
| R2 PUT 请求数（单 app 部分） | ~600 | ~4 |
| R2 上单 app 文件数 | 600 | 600（无孤儿堆积） |

注意：全量包 `full/library-<datasetVersion>.zip` 仍然每次发布都重建（包含所有 app），作为首装与灾备的兜底路径。

## 11. 更新粒度

第一阶段的更新粒度按子数据集分别定义。

### 9.1 catalog 更新粒度

第一阶段按文件集合整体更新，不要求做单字段 delta。

这意味着：

1. 任一 catalog 内容变化，都视为新的 `catalog` 数据快照
2. 第一阶段不定义描述字段级 delta
3. 第一阶段不要求生成 catalog 增量补丁包

### 9.2 library 更新粒度

第一阶段固定为 app 级。

这意味着：

1. 发布系统只判断某个 `apps/<app>` 是否发生变化
2. 一旦某个 app 被识别为变化，就记为该 app 整体更新
3. 不定义 `variables.json`、`.env`、模板等文件级更新类型
4. 不要求生成文件级 delta

允许表达的变更类型只有：

1. `addedApps`
2. `changedApps`
3. `removedApps`

但需要明确区分两层语义：

1. `apps-delta` 只负责表达 app 级变化范围
2. 真正的增量载荷必须由单 app 制品承担

因此客户端更新应采用如下优先级：

1. 首装或本地状态损坏时，下载 `library` 全量包
2. 已有旧版本且服务端提供单 app 制品时，只下载 `addedApps` 与 `changedApps` 对应的 app 包
3. 对 `removedApps` 直接执行本地删除
4. 任一单 app 更新失败时，可回退到全量包恢复

结论：`apps-delta` 不是增量载荷本身；只有在服务端同时发布单 app 制品时，app 级增量更新才成立。

## 12. 版本语义

发布规范中至少区分三类版本语义：

1. `schemaVersion`
2. `datasetVersion`
3. `channel`

且上述版本语义必须分别作用于：

1. `catalog`
2. `library`
3. `appstore` 根级 manifest

定义如下：

1. `schemaVersion` 表达文件结构契约版本，只有结构、字段含义或兼容边界变化时才升级
2. `datasetVersion` 表达该数据集的快照版本，只要内容变化就应生成新的值
3. `channel` 表达稳定性通道，不表达结构版本

额外约束：

1. `catalog` 与 `library` 必须各自拥有独立的 `schemaVersion`
2. `catalog` 与 `library` 必须各自拥有独立的 `datasetVersion`
3. `appstore` 根级 manifest 也必须有自己的 `schemaVersion` 与 `datasetVersion`
4. 普通描述文案变化通常只导致 `catalog.datasetVersion` 与 `appstore.datasetVersion` 变化
5. 安装模板变化通常导致 `library.datasetVersion` 与 `appstore.datasetVersion` 变化
6. 只有 manifest 结构、字段类型、文件布局变化时才升级对应 `schemaVersion`

## 13. Manifest 契约

第一阶段至少定义三层 manifest：

1. `appstore` 根 manifest
2. `catalog` manifest
3. `library` manifest

### 11.1 appstore 根 manifest

最少包含：

1. `schemaVersion`
2. `datasetVersion`
3. `channel`
4. `catalog.manifest`
5. `library.manifest`
6. `generatedAt`

建议样例如下：

```json
{
  "schemaVersion": "1",
  "datasetVersion": "2026.06.09.120000",
  "channel": "release",
  "catalog": {
    "manifest": "catalog/manifest.json"
  },
  "library": {
    "manifest": "library/manifest.json"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 11.2 catalog manifest

最少包含：

1. `schemaVersion`
2. `datasetVersion`
3. `source`
4. `files`
5. `checksum`
6. `generatedAt`

额外要求：

1. `catalog` 必须被定义为独立可版本化的数据集
2. 第一阶段即使仍保留四个兼容 JSON，也必须通过 `catalog/manifest.json` 明确其契约版本边界
3. 后续 catalog 字段演进只能通过 `schemaVersion` 管理，不应直接隐式变更

建议样例如下：

```json
{
  "schemaVersion": "1",
  "datasetVersion": "2026.06.09.120000",
  "source": "contentful",
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
    "productZh": "product_zh.json.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 11.3 library manifest

最少包含：

1. `schemaVersion`
2. `datasetVersion`
3. `channel`
4. `fullPackage`
5. `appsIndex`
6. `appsDelta`
7. `checksum`
8. `generatedAt`

额外要求：

1. `library` 必须被定义为独立可版本化的数据集
2. 第一阶段即使输出仍较简，也必须通过 `library/manifest.json` 明确其契约版本边界
3. 后续 `apps-index`、`apps-delta` 或包命名结构变化只能通过 `schemaVersion` 管理
4. `library manifest` 必须同时暴露全量包入口与单 app 包基准路径
5. `supportsPartialUpdate=true` 才表示客户端可以按 app 制品做网络增量更新
6. 即使支持单 app 更新，仍必须保留全量包作为兜底恢复路径

建议样例如下：

```json
{
  "schemaVersion": "1",
  "datasetVersion": "2026.06.09.120000",
  "channel": "release",
  "fullPackage": {
    "versioned": "full/library-2026.06.09.120000.zip",
    "latest": "full/library-release.zip"
  },
  "appsIndex": "apps-index-2026.06.09.120000.json",
  "appsDelta": "apps-delta-2026.06.08.120000-to-2026.06.09.120000.json",
  "appPackagesBase": "apps/",
  "supportsPartialUpdate": true,
  "checksum": {
    "fullPackageVersioned": "full/library-2026.06.09.120000.zip.sha256",
    "fullPackageLatest": "full/library-release.zip.sha256",
    "appsIndex": "apps-index-2026.06.09.120000.json.sha256",
    "appsDelta": "apps-delta-2026.06.08.120000-to-2026.06.09.120000.json.sha256"
  },
  "generatedAt": "2026-06-09T12:00:00Z"
}
```

### 11.4 apps-index 扩展要求

每个 app 条目最少包含：

1. `app`
2. `hash`
3. `package.latest`
4. `checksum.latest`

说明：

1. `package.latest` 指向该 app 的唯一安装包（`latest.zip`）
2. `hash` 是该 app 目录内容的完整 SHA-256 指纹，客户端通过对比此字段判断 app 是否变更
3. 当 `hash` 与本地记录不同时，客户端下载 `latest.zip` 覆盖本地

## 14. 校验门禁

第一阶段至少执行以下校验：

1. `catalog` 四个核心 JSON 可生成或可拉取
2. `catalog` manifest 字段完整
3. `catalog.schemaVersion` 与 `catalog.datasetVersion` 可追溯
4. `library` 主制品可生成
5. `library` manifest 字段完整
6. `library.schemaVersion` 与 `library.datasetVersion` 可追溯
7. `apps-index` 可生成
8. `apps-delta` 可生成
9. 单 app 制品可按 app 级生成
10. appstore 根 manifest 可生成
11. appstore 根级 `schemaVersion` 与 `datasetVersion` 可追溯
12. 所有 checksum 与实际文件一致
13. R2 上传后的文件可访问
14. legacy catalog 兼容输出可被完整生成
15. legacy library 兼容输出可被完整生成

建议以下情况直接失败：

1. 任一必须制品缺失
2. 任一 manifest 缺关键字段
3. `apps-delta` 不符合 app 级结构
4. 单 app 制品缺失或校验信息不可追溯
5. checksum 不一致
6. 根 manifest 无法追溯到 `catalog` 或 `library`

## 15. 回滚要求

第一阶段的回滚以快照回滚为主。

至少做到：

1. 每次发布保留历史 `appstore-manifest.json`
2. 每次发布保留历史 `catalog` manifest 与对应 JSON
3. 每次发布保留历史 `library` manifest、`apps-index`、`apps-delta`
4. 每次发布保留历史全量 `library` 版本包
5. 每次发布保留历史单 app 版本包
6. 每次发布保留 legacy catalog 与 legacy library 兼容制品
7. 能根据历史根 manifest 找回同一次发布对应的 `catalog` 与 `library` 组合

## 16. 与下游的契约

当前项目与下游系统的契约保持简单：

1. 当前项目负责组装并发布 `appstore` 数据制品
2. `catalog` 与 `library` 的数据边界由 manifest 明确表达
3. 数据发布到 R2 即完成当前项目职责
4. 下游如何消费这些数据，不属于本仓库发布规范
5. legacy 消费者继续消费 legacy 兼容产物，直到迁移窗口结束

## 17. 第一阶段最小改造清单

第一阶段最少只做下面十三件事：

1. 保留 legacy workflow 并允许其在迁移窗口内继续运行
2. 新增独立的 v2 workflow，专门发布 `appstore`
3. 新增 `artifact/websoft9/v2/<channel>/appstore/` 根目录
4. 在根目录下新增 `catalog/`、`library/`、`manifests/` 三层结构
5. 将原先由 `websoft9` 历史流程发布的四个 appstore JSON 纳入当前项目发布职责
6. 为 `catalog`、`library` 与 `appstore` 根级分别建立 `schemaVersion` 和 `datasetVersion` 规则
7. 将旧 library 构建逻辑迁回当前项目内部实现
8. 将旧 catalog 构建逻辑迁回当前项目内部实现
9. 继续保留 legacy 兼容制品
10. 为 `catalog`、`library` 和 `appstore` 根级补充 manifest 与 checksum
11. 保持 `library` 更新粒度为 app 级
12. 为 `library` 增加单 app 制品输出能力
13. 为全量包与单 app 包同时保留版本化对象与最新别名

## 18. 结论

第一阶段的目标不是让当前项目同时承担事实源、消费端和 API 服务，而是在不破坏 legacy 的前提下，把 appstore 的发布职责收回到当前项目，并通过独立的新 workflow 与独立的新目录发布 v2 标准制品。

满足本规范即可认为第一阶段达标：

1. 旧兼容路径继续存在
2. legacy workflow 在并行窗口内继续可用
3. 旧 R2 路径不动
4. v2 使用独立 workflow 与独立 R2 路径
5. 当前项目能够组装 `appstore = catalog + library`
6. `catalog` 与 `library` 都被定义为独立、可版本化的数据集
7. 旧 library 与旧 catalog 兼容制品都可由当前项目独立生成
8. 新增统一的 `appstore/catalog/library/manifests` 目录结构
9. `catalog` 与 `library` 具有清晰的 `schemaVersion` 与 `datasetVersion` 边界
10. `library` 更新粒度固定为 app 级
11. `library` 同时提供全量包与单 app 包两类制品
12. 发布结果可通过根 manifest 追溯到完整发布集合