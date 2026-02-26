# 阶段 1：研究与学习（Research）

## 目标

**从零开始认识一个陌生的应用，并研究其部署方法。**

分为两个层次：
1. **应用认知研究**：了解应用是什么、做什么用、核心特性（为用户提供应用介绍）
2. **部署方法研究**：研究官方安装部署方式、配置要求（为开发计划提供技术数据）

## 执行原则

- 📖 **先认识，再部署**：先理解应用本身，再研究技术实现
- 🎯 **官方优先**：优先使用官方网站、官方文档、官方 Docker 镜像
- 🔍 **主动学习**：从零开始学习陌生应用，不依赖用户提供完整信息
- 📊 **全面理解**：不仅技术层面，也包括业务层面（用途、场景、特性）
- ⚠️ **透明评估**：明确报告信息完整性和理解程度
- 🚫 **不做假设**：不理解的地方明确标记，不编造信息
- 💾 **保存即执行**：每个标记为 `🔒 SAVE` 的保存操作必须立即调用 `create_file` 写入磁盘，不得仅输出到聊天窗口。聊天输出和文件保存是两个独立动作，缺一不可

### 🔒 强制文件保存规则 (MANDATORY)

```
⚠️ 本阶段有 3 个强制保存点，每个都必须调用 create_file 写入实际文件：

保存点 1 (Phase 6):  _bmad-output/workflows/{app_name}/app-introduction.md
保存点 2 (Phase 8):  _bmad-output/workflows/{app_name}/official-compose.yml
保存点 3 (Phase 11): _bmad-output/workflows/{app_name}/state.json

规则:
  ✅ 每个保存点完成后，必须在聊天中确认: "💾 已保存: {文件路径}"
  ❌ 禁止将「保存操作」推迟到后续 Phase 批量执行
  ❌ 禁止仅在聊天中展示内容而跳过 create_file 调用
  ✅ 如果并行执行多个 Phase，保存操作必须在并行完成后立即逐个执行
```

---

## 前置条件

✅ 用户已提供 GitHub Issue URL  
✅ Issue 中包含应用名称（可能还有官方网站）  
✅ 已加载规范文档（`_bmad-output/docker-library-spec.md`）

---

## 研究流程

### 流程概览

```
Part 1: 应用认知研究 ─────────────────────────────────────────
  Phase 1  → Issue 解析 (提取应用名称和参考链接)
  Phase 2  → 官方网站研究 (这是什么应用？)         ┐
  Phase 3  → 核心功能研究 (能做什么？)             ├─ 可并行
  Phase 4  → 使用场景研究 (谁在用？怎么用？)       ├─ fetch_webpage
  Phase 5  → 知名度研究 (成熟吗？活跃吗？)         ┘  批次执行
  Phase 6  → 认知总结 → 输出: app-introduction.md

Part 2: 部署方法研究 ─────────────────────────────────────────
  Phase 7  → 官方部署文档 (怎么装？依赖什么？认证/URL 如何配？)  ┐ 可并行
  Phase 8  → 官方 Compose 研究 [优先] (有官方 compose 吗？)     ┘ 不同URL
  Phase 9  → Docker Hub 研究 [备选] (仅在 Phase 8 不足时执行)
  Phase 10 → 综合分析与规范映射 (W9_* 变量决策)
  Phase 11 → 保存数据与阶段切换 (state.json → step-02-analysis.md)
```

### ⚡ 并行执行策略

> **原则：** 多个独立的 `fetch_webpage` / `github_repo` 调用可以并行发出，减少研究总耗时。

```
批次 1（Phase 1 完成后立即发出）:
  并行请求:
    - fetch_webpage: 官方网站首页          → Phase 2
    - fetch_webpage: 官方网站 /features     → Phase 3
    - fetch_webpage: GitHub README.md       → Phase 3+5
    - fetch_webpage: Docker Hub 页面概览    → Phase 5
  
  ⏱ 预计节省: 从串行 4×3s ≈ 12s → 并行 1×3s ≈ 3s

批次 2（批次 1 结果到达后）:
  并行请求:
    - fetch_webpage: 官方安装文档           → Phase 7
    - github_repo: 搜索 docker-compose.yml  → Phase 8
    - fetch_webpage: Docker Hub tags 页面   → Phase 8 版本确认
  
  ⏱ 预计节省: 从串行 3×3s ≈ 9s → 并行 1×3s ≈ 3s

批次 3（仅在 Phase 8 信息不足时）:
    - fetch_webpage: Docker Hub 详细页面    → Phase 9

注意事项:
  - semantic_search 不可并行，需串行执行
  - 同一域名多个路径可并行（如 example.com/docs 和 example.com/features）
  - 并行结果到达后统一解析，按 Phase 编号逐个填充输出
```

### 💾 研究缓存机制

> **原则：** 每个 Phase 完成后将关键数据写入 state.json 的 `phase_outputs`。恢复中断的研究时，读取缓存跳过已完成的 fetch 操作。

```
缓存策略:

Phase 完成时写入:
  state.json.stage_status.research.phase_outputs.{phase_number} = {
    "completed": true,
    "urls_fetched": ["url1", "url2"],            // 已获取的 URL
    "key_findings": { ... },                      // 提取的关键数据
    "raw_snippets": { "url1": "前500字..." }      // 关键内容片段（限500字/URL）
  }

恢复时检查:
  if phase_outputs[N].completed == true:
    → 跳过 Phase N 的所有 fetch 操作
    → 直接从 phase_outputs[N].key_findings 加载数据
    → 输出: "📋 Phase {N}: 从缓存恢复（{urls_fetched.length} 个URL）"

缓存大小控制:
  - raw_snippets: 每个 URL 最多 500 字（仅保留关键段落）
  - compose 内容: 完整保留（通常 < 5KB）
  - 总缓存: 建议控制在 state.json < 50KB

缓存失效:
  - 用户明确要求 [R] 重新开始 → 清空所有缓存
  - 缓存超过 7 天 → 标记为 stale（仍可用，但输出提示）
```

**关键决策点：**
- Phase 8 找到完整 compose（含明确镜像信息）→ 跳过 Phase 9
- Phase 10 完整度 ≥ 80% → 自动进入分析阶段
- Phase 10 完整度 < 50% → 暂停，要求补充信息

---

### Phase 1: 提取 Issue 基本信息

**输出格式：**
```
🎫 GitHub Issue 解析

应用名称: {app_name}
Issue 标题: {issue_title}
Issue URL: {issue_url}

用户提供的信息:
  官方网站: {official_site} (如果有)
  参考链接: {ref_urls} (如果有)
  简要说明: {user_description} (如果有)

✅ Issue 解析完成

🔍 开始研究陌生应用: {app_name}
```

**提取逻辑：**
1. 从 Issue 标题提取应用名称（去除 "Add", "新增", "Request", "支持" 等前缀）
2. 从 Issue 正文提取官方网站链接
3. 从 Issue 正文提取用户的应用描述（如果有）
4. 提取其他参考链接（GitHub、Docker Hub 等）

**⚠️ Issue 元数据可信度验证（关键步骤）：**
```
Issue 中的结构化字段（如容器数量、依赖列表等）可能是：
  ❌ 模板默认值（用户未修改）
  ❌ 用户的粗略估计
  ❌ 过时信息

验证规则：
  1. 识别模板默认文本（如 "3 containers"、"official architecture research" 等固定句式）
  2. 对以下字段标记为「待验证」而非「事实」：
     - 容器数量:   → 后续 Phase 8/9 自主研究后交叉比对
     - 架构描述:   → 后续 Phase 8 研究后校验
     - Checklist:  → 仅作为参考线索，不作为决策依据
  3. 仅以下字段可直接采信：
     - 应用名称 (Issue 标题)
     - 官方网站 URL (通常准确)
     - source_code_url (通常准确)
```

**已有应用检测（关键步骤）：**
```bash
# 检查 apps/ 目录下是否已存在同名应用
ls apps/{app_name}/ 2>/dev/null

如果已存在:
  ⚠️ 检测到 apps/{app_name}/ 已存在
  
  检查内容是否为模板空壳:
    → .env 中 W9_REPO 是否仍为 "wordpress" (模板默认值)
    → docker-compose.yml 是否仍为 WordPress 配置
    → variables.json 中 release 是否为 false
  
  如果是空壳: → 标记为「覆盖模式」，继续创建
  如果是完整应用: → 提示用户确认是要「更新」还是「重建」
  
如果不存在: → 正常创建模式
```

**心态设定：**
```
⚠️ 假设我们对这个应用完全陌生
⚠️ Issue 中的数据仅作为研究线索，不作为事实
目标：通过研究官方资料，建立对应用的全面认识
```

---

## Part 1: 应用认知研究（了解应用本身）

> **目标：** 从零开始认识这个应用，为用户生成一份应用介绍文档

---

### Phase 2: 官方网站研究

**研究目标：** 了解应用的官方定位和核心介绍

**输出格式：**
```
🌐 官方网站研究

官方网站: {official_site}
官方标语: {tagline}

官方介绍:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{official_description}

这是一个什么样的应用：
- 应用类型: {type} (如: CMS、数据库、协作工具、AI平台)
- 主要用途: {primary_use}
- 目标用户: {target_users}

✅ 官方网站研究完成
```

**研究方法：**
1. 访问官方网站首页（使用 `fetch_webpage`）
2. 提取官方的应用介绍（About、Overview 部分）
3. 理解官方如何定位这个产品
4. 识别应用类型（参考分类：CMS、Database、DevOps、AI、Collaboration 等）

**搜索策略：**
```
如果 Issue 中有官方网站 → 直接访问
如果没有 → 搜索 "{app_name} official website"
         → 或访问常见模式如 https://{app_name}.com, https://{app_name}.org
```

**理解重点：**
- 这个应用**是什么**？
- 这个应用**解决什么问题**？
- **谁会使用**这个应用？

---

### Phase 3: 核心功能与特性研究

**研究目标：** 理解应用的核心功能和主要特性

**输出格式：**
```
⚡ 核心功能与特性

主要功能:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {feature_1}
   说明: {description}
   
2. {feature_2}
   说明: {description}
   
3. {feature_3}
   说明: {description}

技术特性:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 编程语言: {language} (如: PHP, Python, JavaScript, Go)
- 架构模式: {architecture} (如: 单体应用, 微服务)
- 依赖组件: {dependencies} (如: MySQL, Redis, Elasticsearch)
- 许可证: {license} (如: MIT, GPL, Apache 2.0, Commercial)

亮点特性:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- {highlight_1}
- {highlight_2}
- {highlight_3}

✅ 功能特性研究完成
```

**研究方法：**
1. 查看官方网站的 Features 页面
2. 阅读官方文档的 Overview/Introduction 章节
3. 查看 GitHub 仓库的 README.md
4. 识别技术栈（从文档或代码仓库）

**理解重点：**
- 这个应用能**做什么**？
- 有哪些**核心能力**？
- 技术实现基于什么**技术栈**？

---

### Phase 4: 使用场景研究

**研究目标：** 理解应用的典型使用场景

**输出格式：**
```
🎯 典型使用场景

适用场景:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {use_case_1}
   示例: {example}
   
2. {use_case_2}
   示例: {example}
   
3. {use_case_3}
   示例: {example}

行业应用:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- {industry_1}: {application}
- {industry_2}: {application}

对比竞品:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
与 {competitor_1} 相比: {difference}
与 {competitor_2} 相比: {difference}

✅ 使用场景研究完成
```

**研究方法：**
1. 查看官方网站的 Use Cases / Solutions 页面
2. 阅读官方博客的案例文章
3. 搜索 "{app_name} use cases" 或 "{app_name} examples"
4. 了解主要竞争对手（可选）

**理解重点：**
- 这个应用在**什么场景下**使用？
- **谁**在实际使用它？
- 相比其他同类产品有什么**优势**？

---

### Phase 5: 知名度与生态研究

**研究目标：** 评估应用的成熟度和社区活跃度

**输出格式：**
```
📈 知名度与生态评估

项目成熟度:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 首次发布: {first_release_year}
- 开发状态: [✅ 活跃维护 / ⚠️ 缓慢更新 / ❌ 停止维护]
- 最新版本: {latest_version} (发布于 {release_date})

社区活跃度 (如果是开源):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- GitHub Stars: {stars}
- GitHub Forks: {forks}
- Contributors: {contributors}
- Issues: {open_issues} 开放, {closed_issues} 已关闭

用户规模:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 知名用户: {notable_users} (如果官方列出)
- 下载量: {download_count} (如果可获取)
- Docker Hub 拉取: {docker_pulls}

生态系统:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 插件/扩展: [✅ 丰富 / ⚠️ 一般 / ❌ 较少]
- 文档质量: [✅ 完善 / ⚠️ 一般 / ❌ 缺失]
- 社区支持: [✅ 活跃 / ⚠️ 一般 / ❌ 冷清]

✅ 生态评估完成
```

**研究方法：**
1. 访问 GitHub 仓库（如果是开源项目）
2. 查看 Docker Hub 的镜像拉取次数
3. 搜索应用的用户案例或客户列表
4. 评估文档完整性

**理解重点：**
- 这个应用**成熟吗**？
- **社区活跃**吗？
- 是否有**良好的生态支持**？

---

### Phase 6: 应用认知总结

**输出格式：**
```
╔════════════════════════════════════════════════════════════╗
║                应用认知研究总结                              ║
╚════════════════════════════════════════════════════════════╝

📋 应用档案
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
名称: {app_name}
类型: {type}
官方网站: {official_site}
开源协议: {license}
技术栈: {tech_stack}

📖 一句话介绍
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{one_sentence_intro}

🎯 核心价值
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{core_value_proposition}

✨ 主要特点
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. {key_feature_1}
2. {key_feature_2}
3. {key_feature_3}

👥 典型用户
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{target_audience}

📊 成熟度评估
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
项目成熟度: ⭐⭐⭐⭐⭐ ({rating}/5)
社区活跃度: ⭐⭐⭐⭐⭐ ({rating}/5)
文档完整性: ⭐⭐⭐⭐⭐ ({rating}/5)
推荐程度: [✅ 推荐 / ⚠️ 谨慎 / ❌ 不推荐]

════════════════════════════════════════════════════════════

✅ Part 1 完成 - 我们现在理解了 {app_name} 是什么

📝 应用介绍文档已生成，保存到:
   _bmad-output/workflows/{app_name}/app-introduction.md

🔄 继续 Part 2: 研究部署方法
```

**🔒 SAVE — 保存点 1 (MANDATORY)：**

```
🚨 此处必须立即调用 create_file 将文档写入磁盘，不得跳过！

文件: _bmad-output/workflows/{app_name}/app-introduction.md
内容: Phase 2-6 研究结果的完整 Markdown 文档
包含: 应用概述、核心功能、使用场景、技术特性、适用人群

执行后确认: 在聊天中输出 "💾 已保存: app-introduction.md"
```

**这份文档的用途：**
- 帮助用户快速了解应用
- 为 README.md 提供介绍内容
- 为分析阶段提供业务背景

---

## Part 2: 部署方法研究（研究安装部署）

> **目标：** 研究官方推荐的安装部署方式，收集技术实现数据

---

### Phase 7: 官方部署文档研究

**研究目标：** 了解官方推荐的安装部署方式和要求

**输出格式：**
```
📚 官方部署文档研究

文档地址: {installation_doc_url}

官方支持的部署方式:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✅/❌] Docker / Docker Compose
[✅/❌] Kubernetes / Helm
[✅/❌] 传统安装 (apt/yum/源码编译)
[✅/❌] 云服务 (AWS/Azure/GCP)
[✅/❌] SaaS 托管服务

官方推荐: {recommended_deployment_method}
Docker 支持: [✅ 官方支持 / ⚠️ 社区支持 / ❌ 不支持]

系统要求:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 最低配置: {min_cpu} CPU, {min_ram} RAM, {min_disk} 磁盘
- 推荐配置: {rec_cpu} CPU, {rec_ram} RAM, {rec_disk} 磁盘
- 支持的操作系统: {supported_os}

依赖说明:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- 数据库: {database_requirement} (如: MySQL 8.0+, PostgreSQL 12+)
- 缓存: {cache_requirement} (如: Redis 6.0+)
- 其他依赖: {other_dependencies}

✅ 官方部署文档研究完成
```

**研究方法：**
1. 查找官方文档的 Installation / Deployment / Getting Started 章节
2. 识别官方推荐的部署方式（优先关注 Docker 相关）
3. 了解系统要求和依赖组件
4. 确认 Docker 部署是否官方支持

**理解重点：**
- 官方**推荐**用什么方式部署？
- Docker 部署是否是**官方支持**的方式？
- 有什么**依赖要求**（数据库、缓存等）？

**同时关注以下关键配置信息（为 Phase 10 分析做准备）：**

```
认证配置检测:
  查找文档中是否提到以下内容:
  - 初始管理员账户设置 (initial admin, default password)
  - 管理员环境变量 (ADMIN_USER, ADMIN_PASSWORD, ROOT_PASSWORD)
  - 首次登录设置向导
  → 记录: 是否支持通过环境变量预配置管理员？[是/否]

URL 配置检测:
  查找文档中是否提到以下内容:
  - 外部访问 URL 配置 (external URL, base URL, site URL)
  - 信任域名配置 (trusted domains)
  - 回调/Webhook URL 要求
  → 记录: 是否需要配置外部访问 URL？[是/否]

环境变量文档:
  记录所有找到的环境变量，特别关注:
  - 数据库连接变量 (DB_HOST, DB_PASSWORD, etc.)
  - 应用配置变量 (APP_*, SERVER_*, etc.)
  - 密钥/密码变量 (SECRET_KEY, API_KEY, etc.)
```

---

### Phase 8: 官方 Docker Compose 研究（优先）

**研究目标：** 查找并解析官方 docker-compose.yml（优先级最高，包含完整部署信息）

**输出格式：**
```
� 官方 Docker Compose 研究

查找范围:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✅/❌] 官方 GitHub 仓库
[✅/❌] 官方文档示例
[✅/❌] Docker Hub 描述页
[✅/❌] examples/ 或 docker/ 目录

查找结果:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[✅ 找到 / ❌ 未找到] 官方 docker-compose.yml

来源信息 (如果找到):
  来源类型: [✅ 官方仓库 / ⚠️ 官方文档 / 📦 社区示例]
  文件位置: {source_url}
  维护状态: [✅ 活跃维护 / ⚠️ 较旧 / ❌ 已废弃]
  最后更新: {last_updated}

服务架构概览:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
服务总数: {service_count} 个

主要服务及镜像:
  1. {service_1}
     镜像: {image}:{version}
     镜像来源: [✅ Docker Official / ⚠️ Verified Publisher / 📦 Community / 🔨 自定义]
     端口: {ports}
     卷: {volumes}
  
  2. {service_2} (如果有)
     镜像: {image}:{version}
     镜像来源: [同上标注]
     端口: {ports}
     卷: {volumes}

服务依赖关系:
  {service_1} → depends_on → {service_2}

镜像信息汇总:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
主应用镜像: {main_image}:{version}
镜像类型: [✅ Docker Official / ⚠️ Verified Publisher / 📦 Community / 🔨 自定义镜像]
版本指定: [✅ 固定版本号 / ⚠️ 使用 latest / ⚠️ 无版本标签]

✅ 官方 Compose 研究完成
```

**研究方法（按优先级）：**

**第一优先级：官方 GitHub 仓库**
1. 使用 `github_repo` 搜索官方仓库中的 docker-compose.yml
2. 查找位置：
   - `/docker-compose.yml` (仓库根目录)
   - `/examples/docker-compose.yml`
   - `/docker/docker-compose.yml`
   - `/deploy/docker-compose.yml`

**第二优先级：官方文档**
1. 使用 `fetch_webpage` 获取官方文档
2. 搜索 "docker compose" 或 "docker-compose" 示例
3. 提取文档中的完整 compose 配置

**第三优先级：Docker Hub**
1. 访问 Docker Hub 镜像页面
2. 查看 "How to use this image" 部分
3. 提取 docker-compose 示例（如果有）

**⚠️ Compose 类型判断（关键步骤）：**
```
找到 compose 后，先判断其类型：

[类型 A] 产品级 Compose — 可直接作为改造基准
  特征: 服务数 ≤ 10，镜像使用预构建标签，面向最终用户部署
  示例: WordPress (wordpress + mysql)，GitLab (gitlab-ce)
  动作: → 正常提取信息，作为 Phase 4 改造基准

[类型 B] Demo/示例 Compose — 不能直接作为改造基准
  特征: 服务数 > 10，包含大量微服务，用于演示/教学
         或包含 build: 指令，需要本地构建
  示例: OpenTelemetry Demo (25+ 容器), Microservices Demo
  动作: → 标记为「Demo 架构」
        → 不作为改造基准
        → 需要在 Phase 10 中决定 docker-library 的部署范围
        → 🚨 必须在 Phase 10g 中明确提示用户确认架构选择

[类型 C] 最小化示例 — 需要补充完善
  特征: 仅 1-2 个服务，缺少推荐的依赖（如缺少数据库）
  示例: 仅有 app 容器，文档建议搭配 PostgreSQL 但 compose 中未包含
  动作: → 以此为基础，根据文档补充依赖服务
```

**从 Compose 中提取的信息：**
```
✅ 如果找到官方 compose:
  - Compose 类型: [A 产品级 / B Demo / C 最小化]
  - 主应用镜像名称和版本 (从 image: 字段)
  - 依赖服务镜像 (数据库、缓存等)
  - 环境变量列表
  - 卷映射关系
  - 网络配置
  - 端口映射
  
→ 类型 A: 镜像信息已获取，Phase 9 可能跳过或简化
→ 类型 B: 需要 Phase 10 重新定义部署范围
→ 类型 C: 需要 Phase 9 补充依赖镜像信息
```

**镜像来源标注规则：**
```yaml
# ✅ Docker Official Image
image: wordpress:6.9
→ 标注: ✅ Docker Official (https://hub.docker.com/_/wordpress)

# ⚠️ Verified Publisher
image: gitlab/gitlab-ce:18.1.3-ce.0
→ 标注: ⚠️ Verified Publisher (https://hub.docker.com/r/gitlab/gitlab-ce)

# 📦 Community/Personal
image: bitnami/wordpress:6.9
→ 标注: 📦 Community (bitnami 维护)

# 🔨 自定义构建
image: ./Dockerfile 或 build: .
→ 标注: 🔨 自定义镜像 (需要构建，存在风险)
```

**如果未找到官方 Compose：**
```
❌ 未找到官方 docker-compose.yml

尝试的位置:
  - GitHub 仓库 (根目录、examples/、docker/)
  - 官方文档 (Installation、Deployment 章节)
  - Docker Hub (镜像说明页)

结论: 需要单独查找镜像信息

→ 继续执行 Phase 9 (Docker Hub 镜像研究)
```

**🔒 SAVE — 保存点 2 (MANDATORY)：**

```
🚨 此处必须立即调用 create_file 将 compose 写入磁盘，不得跳过！

文件: _bmad-output/workflows/{app_name}/official-compose.yml
内容: 官方 docker-compose.yml 原始内容（含文件头注释标注来源 URL 和获取日期）

执行后确认: 在聊天中输出 "💾 已保存: official-compose.yml"
如果未找到官方 compose: 跳过此保存点，在聊天中说明原因
```

- 这将作为 Phase 3 (Development) 的**参考基准**

---

### Phase 9: Docker Hub 镜像研究（备选/补充）

**研究目标：** 仅在 Phase 8 未找到 compose 或需要补充镜像信息时执行

**执行条件：**
```
条件 1: Phase 8 未找到官方 docker-compose.yml
条件 2: Phase 8 找到 compose，但镜像信息不完整（使用变量或自定义构建）
条件 3: 需要确认镜像的最新稳定版本

如果 Phase 8 已找到完整的 compose (包含明确的镜像名称和版本):
  → ⏭️ 跳过 Phase 9，直接进入 Phase 10
```

**输出格式：**
```
🐳 Docker Hub 镜像研究

前置检查:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 8 结果: [✅ 找到 compose / ❌ 未找到 compose]
Compose 中镜像信息: [✅ 明确 / ⚠️ 不完整 / ❌ 无]
执行原因: {why_needed}

搜索关键词: {app_name}

找到的镜像:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
镜像名称: {image_name}
镜像类型: [✅ Docker Official / ⚠️ Verified Publisher / 📦 Community / 🔨 自定义]
  └─ 识别依据: {reason}

Docker Official: {official_name}   (如: wordpress, nginx, mysql)
  URL: https://hub.docker.com/_/{official_name}
  信任度: ✅ 最高 (Docker 官方维护)

Verified Publisher: {org}/{image}  (如: gitlab/gitlab-ce)
  URL: https://hub.docker.com/r/{org}/{image}
  信任度: ⚠️ 中等 (组织认证)

Community: {user}/{image}          (如: bitnami/wordpress)
  URL: https://hub.docker.com/r/{user}/{image}
  信任度: 📦 取决于维护者 (检查星数和下载量)

自定义构建: build: ./Dockerfile
  信任度: 🔨 需要审查 (本地构建，可能存在安全风险)

版本信息:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
最新稳定版: {latest_stable_version}
选择理由: {reason}
可用标签: {tag_1}, {tag_2}, {tag_3}, ...
最后更新: {last_updated}
总拉取量: {total_pulls}

版本分支 (如果有):
  - Community Edition: {ce_image}:{ce_version}
  - Enterprise Edition: {ee_image}:{ee_version}
  - Alpine 变种: {image}:{version}-alpine

多镜像对比 (如有多个候选):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
选项  |  镜像名称         |  类型      |  拉取量  |  推荐度
1     |  {image_1}        |  Official  |  100M+   |  ✅ 推荐
2     |  {image_2}        |  Verified  |  50M+    |  ⚠️ 次选
3     |  {image_3}        |  Community |  10M+    |  📦 备选

最终选择: {chosen_image}:{chosen_version}
  选择原因: {detailed_reason}

✅ Docker Hub 研究完成
```

**镜像类型识别方法：**

```bash
# 检查方法 1: 镜像名称格式

✅ Docker Official Image:
  镜像名: wordpress, nginx, mysql, postgres (无组织前缀)
  URL 格式: https://hub.docker.com/_/{image_name}
  特征: "Docker Official Image" 徽章
  
⚠️ Verified Publisher:
  镜像名: gitlab/gitlab-ce, bitnami/postgresql (org/image格式)
  URL 格式: https://hub.docker.com/r/{org}/{image}
  特征: "Verified Publisher" 徽章 + 组织认证
  
📦 Community Image:
  镜像名: jwilder/nginx-proxy, linuxserver/plex (user/image格式)
  URL 格式: https://hub.docker.com/r/{user}/{image}
  特征: 无特殊徽章，由个人或社区维护
  
🔨 Custom Build:
  定义: build: . 或 build: ./path/to/Dockerfile
  特征: 需要本地构建，无 Docker Hub 页面
```

**版本选择原则：**
```
✅ 推荐:
  - 使用明确的版本号: 6.9, 18.1.3-ce.0, 2.7.1
  - 选择最新的稳定版本 (排除 beta, rc, nightly)
  
⚠️ 避免:
  - latest 标签 (不利于版本控制和复现)
  - dev, nightly, edge 等开发版本标签
  - 超过 6 个月未更新的版本 (可能已废弃)

```

**版本获取方法（多源验证）：**
```
Docker Hub API 查询:
  curl -s "https://registry.hub.docker.com/v2/repositories/{image}/tags/?page_size=50&ordering=last_updated"
  → 过滤: 排除 sha256-*, nightly*, *-rc*, latest
  → 选择: 第一个符合 语义版本 (X.Y.Z) 格式的标签

如果 API 返回结果不明确:
  → 检查 GitHub Releases 页面 (通常与镜像版本同步)
  → 检查官方文档中推荐的版本号

⚠️ 对多镜像应用 (如 app + db + cache):
  → 每个镜像独立验证版本
  → 记录各镜像版本到 research_data
  → 不可互相推测版本 (如 Jaeger 版本不能从 OTel 版本推断)
```🔍 检查变种:
  - 标准版 vs Alpine 版 (体积更小，但兼容性可能有差异)
  - Community vs Enterprise (功能差异)
  - 不同数据库支持 (mysql vs postgres)
```

**研究方法：**
1. 使用 `fetch_webpage` 获取 Docker Hub 页面
2. 搜索官方镜像 (https://hub.docker.com/_/{app_name})
3. 如无官方镜像，搜索 Verified Publisher
4. 提取标签列表和版本信息
5. 检查镜像维护状态和更新频率

**映射到规范：**
```bash
# .env 变量映射
W9_REPO={image_name}     # 如: wordpress, gitlab/gitlab-ce, bitnami/mysql
W9_VERSION={version}     # 如: 6.9, 18.1.3-ce.0, 8.0.36

# 示例:
Docker Official → W9_REPO=wordpress, W9_VERSION=6.9
Verified Pub    → W9_REPO=gitlab/gitlab-ce, W9_VERSION=18.1.3-ce.0
Community       → W9_REPO=bitnami/mysql, W9_VERSION=8.0.36
```

**保存操作（可选）：**
- 如果执行了 Phase 9，保存镜像元数据：`_bmad-output/workflows/{app_name}/docker-hub-research.md`
- 记录镜像类型、版本选择理由、备选方案
- 注：Phase 9 为备选步骤，此保存点非强制

---

### Phase 10: 综合分析与规范映射

**分析目标：** 基于 Phase 7-9 收集的原始数据，执行系统分析并做出 W9_* 变量决策

> 这是研究阶段最关键的分析步骤。所有条件变量（W9_LOGIN_*, W9_URL_REPLACE）的最终决策都在这里做出。

---

#### Step 10a: 环境变量分类

将 Phase 7-9 中收集的所有环境变量按用途分类：

| 分类 | 检测模式 | 映射规则 |
|------|---------|----------|
| 数据库 | `*DB_HOST*`, `*DB_PASSWORD*`, `*MYSQL_*`, `*POSTGRES_*`, `*MONGO_*` | 密码统一使用 `$W9_POWER_PASSWORD` |
| 认证 | `*ADMIN_USER*`, `*ADMIN_PASSWORD*`, `*ROOT_PASSWORD*`, `*ADMIN_EMAIL*` | → Step 10b 决策 |
| URL | `*SITE_URL*`, `*BASE_URL*`, `*EXTERNAL_URL*`, `*TRUSTED_DOMAIN*` | → Step 10c 决策 |
| 密钥 | `*SECRET_KEY*`, `*JWT_SECRET*`, `*API_KEY*` | 使用 `$W9_POWER_PASSWORD` 或自动生成 |
| 应用特定 | 不匹配以上模式的变量 | 保留原值或设置合理默认值 |

---

#### Step 10b: W9_LOGIN_* 决策

**决策树（基于统计: 39.9% 的现有应用使用此变量）：**

```
检测优先级:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] 显式管理员环境变量 (置信度 95%)
    匹配: *ADMIN_USER*, *ADMIN_PASSWORD*, *ADMIN_EMAIL*
           *ROOT_PASSWORD*, *INITIAL_ADMIN*, *DEFAULT_USER*
    → ✅ 需要 W9_LOGIN_USER + W9_LOGIN_PASSWORD

[2] 应用特定管理员变量 (置信度 90%)
    匹配: WORDPRESS_ADMIN_*, GITLAB_ROOT_*, GRAFANA_ADMIN_*
           JENKINS_ADMIN_*, KEYCLOAK_ADMIN_*, ODOO_ADMIN_*
    → ✅ 需要

[3] 文档提到初始管理员配置 (置信度 85%)
    条件: 官方文档提到 "initial admin" / "default password"
           且可通过环境变量预配置
    → ✅ 需要

[4] 无认证 / 仅 Token / API Key (置信度 90%)
    条件: 无上述模式，仅有 API_KEY / SECRET_TOKEN 等
    → ❌ 不需要 W9_LOGIN_*

[5] 首次访问时手动创建 (置信度 85%)
    条件: 文档指示"首次访问时设置密码"，无预配置环境变量
    → ❌ 不需要 W9_LOGIN_*

[6] 无任何认证系统 (置信度 95%)
    条件: 静态站点、工具类、无用户管理
    → ❌ 不需要 W9_LOGIN_*
```

**执行：** 输出匹配到的模式编号、证据和最终决定。

---

#### Step 10c: W9_URL_REPLACE 决策

**决策树（基于统计: 33.6% 的现有应用使用此变量）：**

```
检测优先级:
━━━━━━━━━━━━━━━━━━━━━━━━━━━

[1] Compose 中直接引用 $W9_URL (置信度 100%)
    示例: NEXTCLOUD_TRUSTED_DOMAINS=$W9_URL
    → ✅ 需要 W9_URL_REPLACE=true

[2] 外部 URL 环境变量 (置信度 95%)
    匹配: *TRUSTED_DOMAIN*, *EXTERNAL_URL*, *SITE_URL*
           *BASE_URL*, *PUBLIC_URL*, *SERVER_URL*
    → ✅ 需要 (需将 $W9_URL 注入到对应变量)

[3] 回调/Webhook URL 需求 (置信度 90%)
    匹配: *CALLBACK_URL*, *WEBHOOK_URL*, *REDIRECT_URI*
    → ✅ 需要

[4] 无 URL 相关配置 (置信度 90%)
    条件: 无上述模式
    → ❌ 不需要 W9_URL_REPLACE
    注意: W9_URL 仍保留在 .env 中，但不设置 W9_URL_REPLACE
```

**执行：** 输出匹配到的模式编号、证据和最终决定。

---

#### Step 10d: src/ 文件与卷映射分析

```
从 Phase 8 的 compose volumes 中提取:

配置文件映射 (需要创建 src/ 文件):
  规则: volumes 中 ./src/*:容器路径 的映射 → 必须创建对应文件
  [ ] src/{file1} - {用途说明}
  [ ] src/{file2} - {用途说明}
  [ ] src/README.md - 配置文件说明文档

数据卷 (命名卷，不需要 src/ 文件):
  - {volume_name}:{container_path}
```

---

#### Step 10e: 复杂度与测试策略评估

```
评分维度:
  服务数量:   1个=5, 2-3个=15, 4-6个=20, 7+=25     → {score}/25
  环境变量:   <5=5, 5-15=15, 15-30=20, 30+=25       → {score}/25
  配置文件:   0=0, 1-3=10, 4-6=20, 7+=25            → {score}/25
  特殊需求:   无=0, 初始化脚本=10, 自定义构建=15     → {score}/25

  总分: {total}/100
  等级: 简单(0-25) / 标准(26-50) / 复杂(51-75) / 非常复杂(76-100)
  测试层: L1(静态验证) + L2(部署验证) + L3(人工功能验证，复杂度>50时必须)
```

---

#### Step 10f: 信息完整度评估

```
核心信息:                          权重    状态
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker 镜像名称和版本              25%    [✅/❌]
基本服务架构                       20%    [✅/❌]
官方 docker-compose.yml           20%    [✅/⚠️/❌]
环境变量列表                       15%    [✅/⚠️/❌]
认证/URL 配置需求                  10%    [✅/⚠️/❌]
卷映射和配置文件                    10%    [✅/⚠️/❌]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
完整度: {percentage}%

决策:
  ≥ 80% → ✅ 自动继续到分析阶段
  50-79% → ⚠️ 询问用户是否继续
  < 50% → ❌ 暂停，要求补充信息或参考类似应用
```

**完整度不足时，参考类似应用：**
- 使用 `grep_search` 在 `apps/*/.env` 中搜索同类型应用的 W9_* 配置
- 使用 `semantic_search` 查找同类别应用（CMS、数据库、AI 工具等）
- 参考同类应用的 W9_LOGIN_* / W9_URL_REPLACE / src/ 目录模式

---

#### Step 10g: 研究摘要输出

**⚠️ Compose 类型 B (Demo) 时的架构决策门控：**
```
如果 Phase 8 判定为 类型 B (Demo/示例 Compose):

🚨 架构决策需要用户确认 — 不可自行决定

展示给用户:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
检测到: 官方 compose 为 Demo/演示架构 ({service_count} 个容器)
原因: {为什么判定为 Demo — 容器数 >10 / 包含大量微服务 / 需要 build}

docker-library 中需要决定部署范围，可选方案:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{根据研究自动生成合理方案列表}

  [A] {方案A名称} — {容器数}容器
      包含: {服务列表}
      定位: {方案说明}
  
  [B] {方案B名称} — {容器数}容器
      包含: {服务列表}
      定位: {方案说明}
  
  [C] 自定义 — 用户指定包含哪些服务

⚠️ 仅在用户明确选择后，才以选定方案作为后续分析基准
⚠️ 将用户选择记录到 state.json: architecture_decision.user_choice
```

**输出格式：**
```
╔════════════════════════════════════════════════════════════╗
║          阶段 1 研究完成 - 应用信息摘要                      ║
╚════════════════════════════════════════════════════════════╝

📦 应用基本信息
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
名称: {app_name}
镜像: {image}:{version}
镜像来源: [✅ Docker Official / ⚠️ Verified Publisher / 📦 Community]
类别: {category}
架构: {architecture_summary}

🧩 模式匹配 (来自 _bmad/bmb/knowledge/app-patterns.yaml)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
匹配模式: Pattern {id} - {pattern_name}
参考应用: {reference_apps}（建议查看其 .env 和 compose 配置）
常见陷阱: {common_pitfalls}

💡 先例参考 (来自 _bmad/bmb/knowledge/decision-precedents.yaml)
  W9_LOGIN 最相似先例: {similar_app} — {decision} (rule: {rule_id})
  W9_URL   最相似先例: {similar_app} — {decision} (rule: {rule_id})

🔧 配置复杂度
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
服务数量: {service_count}
环境变量: {env_count} 个
卷映射: {volume_count} 个
src/ 文件: {src_files_count} 个
复杂度等级: {简单/标准/复杂/非常复杂}
测试层级: Tier {A/B/C/D}

📊 规范映射决策 (基于 Step 10b/10c 分析)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
W9_LOGIN_USER/PASSWORD: [✅ 需要 / ❌ 不需要] ({confidence}%)
  匹配模式: {matched_pattern} | 依据: {evidence}
W9_URL_REPLACE:         [✅ 需要 / ❌ 不需要] ({confidence}%)
  匹配模式: {matched_pattern} | 依据: {evidence}
src/ 目录:              [✅ 需要 / ❌ 不需要]
  文件列表: {files_list}

🎯 关键发现
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ {key_finding_1}
✅ {key_finding_2}
⚠️ {concern_1} (如果有)

� Issue 声明 vs 研究结论交叉验证
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{对 Issue 中的每个可验证声明，与研究结果比对}

  Issue 声明            | 研究结论           | 匹配
  容器数: {issue_count} | 实际: {real_count} | [✅ 一致 / ❌ 冲突 / ⚠️ 模板默认值]
  {其他可验证字段...}

{如果有 ❌ 冲突或 ⚠️ 模板默认值}
  ⚠️ 以研究结论为准，Issue 数据已标记为不可靠
{end}

�📁 数据来源
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Docker Hub: {url}
GitHub: {url}
官方文档: {url}
官方 Compose: {url}

════════════════════════════════════════════════════════════

✅ 研究阶段完成 - 信息完整度: {percentage}%

下一步: 生成应用开发计划文档（阶段 2）

继续到分析阶段? [Y/n]
```

**如果用户确认 (Y 或直接回车)：**
- 保存研究数据到工作流状态
- 加载 `step-02-analysis.md`

**如果用户取消 (n)：**
```
⏸️  工作流已暂停

研究数据已保存到: {state_file}

您可以随时使用以下命令继续:
  [CA] Create App - 从当前阶段继续
  [ST] Status - 查看工作流状态

或者:
  [AN] Analyze - 分析其他现有应用
  [RS] Restart - 重新开始研究
```

---

### Phase 11: 保存研究数据与阶段切换

**状态文件路径：** `_bmad-output/workflows/{app_name}/state.json`

**数据结构：**
```json
{
  "workflow_id": "{uuid}",
  "app_name": "{app_name}",
  "created_at": "{timestamp}",
  "current_stage": "research",
  "stage_status": {
    "research": "completed",
    "analysis": "pending",
    "development": "pending",
    "testing": "pending"
  },
  "research_data": {
    "basic_info": {
      "app_name": "",
      "image": "",
      "version": "",
      "image_source": "docker_official|verified_publisher|community|custom",
      "category": "",
      "official_site": "",
      "github_repo": "",
      "docker_hub_url": ""
    },
    "architecture": {
      "service_count": 0,
      "services": [],
      "main_service": "",
      "dependencies": []
    },
    "official_compose": {
      "found": true,
      "source_url": "",
      "source_type": "github_repo|official_docs|docker_hub|community",
      "compose_type": "A_production|B_demo|C_minimal",
      "content": ""
    },
    "architecture_decision": {
      "source": "official_compose|user_choice|research_based",
      "user_choice": null,
      "user_choice_reason": ""
    },
    "issue_metadata_validation": {
      "container_count_claim": null,
      "container_count_actual": null,
      "claim_reliable": false,
      "notes": ""
    },
    "existing_app_detected": {
      "exists": false,
      "is_template_shell": false,
      "action": "create|overwrite|update"
    },
    "environment_variables": [
      {
        "name": "",
        "value": "",
        "category": "database|auth|url|secret|app_specific",
        "source": "official_compose|docs|docker_hub"
      }
    ],
    "volume_mappings": [
      {
        "local": "",
        "container": "",
        "type": "config|data",
        "needs_src_file": true
      }
    ],
    "compliance_prediction": {
      "w9_login_user": {
        "required": true,
        "confidence": 0.95,
        "matched_pattern": "[1-6]",
        "reason": "",
        "evidence": ""
      },
      "w9_url_replace": {
        "required": true,
        "confidence": 0.90,
        "matched_pattern": "[1-4]",
        "reason": "",
        "evidence": ""
      },
      "src_directory": {
        "required": true,
        "files": []
      }
    },
    "complexity_assessment": {
      "score": 0,
      "level": "simple|standard|complex|very_complex",
      "test_tier": "A|B|C|D"
    },
    "information_completeness": {
      "percentage": 0,
      "risk_level": "low|medium|high",
      "missing_items": [],
      "concerns": []
    }
  }
}
```

**🔒 SAVE — 保存点 3 (MANDATORY)：**

```
🚨 此处必须立即调用 create_file 将 state.json 写入磁盘！
🚨 此保存点必须在询问用户 [Y/n] 之前完成，确保中断恢复时数据不丢失。

文件: _bmad-output/workflows/{app_name}/state.json
内容: 完整的工作流状态 JSON（含 research_data 全部字段）

执行后确认: 在聊天中输出 "💾 已保存: state.json"
```

**保存验证检查清单（阶段切换前必须全部通过）：**
```
[ ] app-introduction.md — 已通过 create_file 写入磁盘
[ ] official-compose.yml — 已写入 或 已标注「未找到」原因
[ ] state.json — 已通过 create_file 写入磁盘

如果任一文件未保存 → 立即补救，不得进入阶段 2
```

**阶段切换：**

触发条件：用户确认继续 或 信息完整度 ≥ 80%

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
阶段切换: Research → Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 研究数据已保存
🔄 加载: _bmad/bmb/workflows/app-curator/steps/step-02-analysis.md
```

传递数据：完整的 `research_data` 对象 + 工作流状态文件路径

执行：
```markdown
读取并执行: ./step-02-analysis.md
```

---

## 参考信息

### 成功标准

**必须完成：**
- [ ] 提取应用名称和基本信息 (Phase 1)
- [ ] 生成应用认知总结 (Phase 6 → app-introduction.md)
- [ ] 确定官方 Docker 镜像和版本 (Phase 8/9)
- [ ] 完成 W9_* 变量决策并记录依据 (Phase 10)
- [ ] 评估信息完整性 ≥ 50% (Phase 10f)
- [ ] 保存研究数据到 state.json (Phase 11)

**推荐完成：**
- [ ] 找到官方 docker-compose.yml (Phase 8)
- [ ] 解析环境变量并完成分类 (Phase 10a)
- [ ] 参考类似应用验证决策 (Phase 10f)
- [ ] 明确 src/ 文件清单 (Phase 10d)

### 错误处理

| 场景 | 处理策略 |
|------|----------|
| 找不到官方镜像 | 暂停工作流，请求用户确认应用名称或提供 Docker Hub 链接 |
| 官方 Compose 过于复杂 (>10 服务) | 提示用户选择：继续简化/手动提供/参考社区版本 |
| 信息严重不足 (<50%) | 暂停，建议：补充链接/选择参考模板/改为手动创建 |
| 镜像超过 6 个月未更新 | 标记风险警告，继续但在摘要中注明 |

### 质量检查（进入下一阶段前）

```
基本信息:  [✅] 应用名称  [✅] Docker 镜像和版本  [✅] 基本架构
规范映射:  [✅] W9_LOGIN_* 决策  [✅] W9_URL_REPLACE 决策  [✅] src/ 文件清单
数据保存:  [✅] state.json  [✅] 来源 URL 已记录
总体评估:  [通过/需改进]
```

---

## 输出示例 (WordPress)

```
╔════════════════════════════════════════════════════════════╗
║          阶段 1 研究完成 - WordPress                     ║
╚════════════════════════════════════════════════════════════╝

📦 应用: WordPress | CMS | 镜像: wordpress:6.9 (✅ Docker Official)
🏗️ 架构: 2 服务 (应用 + MySQL) | 复杂度: 标准(35/100) | L3 建议

📊 规范映射决策:
  W9_LOGIN_USER/PASSWORD: ✅ 需要 (90%) - wp-cli 可预配置管理员
  W9_URL_REPLACE:         ✅ 需要 (95%) - WordPress 将 URL 写入数据库
  src/ 目录:              ❌ 不需要 - 无配置文件映射

🎯 关键发现:
  ✅ 找到官方 docker-compose.yml
  ✅ 数据库: MySQL 8.0 + 健康检查
  ⚠️ 官方 compose 未使用 external network，需调整

📁 信息完整度: 95% | 继续到分析阶段? [Y/n]
```

---

**注意事项：**
- 此阶段仅收集信息，不生成任何应用文件
- 所有 W9_* 判断都是"预测"，最终决策在分析阶段确认
- 透明度优先：明确告知信息来源和置信度

**下一阶段预览：** 阶段 2 将使用研究数据生成详细的应用开发计划文档。
