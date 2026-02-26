# {{ app_name }} 应用开发计划

<!--
模板使用说明：
- 由 step-02 Phase 8a 的 AI 代理填充生成（非 Jinja2 引擎）
- {{ variable }} = 替换为具体值
- {% if/for %} = AI 根据条件判断是否包含该内容
- 📌 标记 = step-03 直接从该章节提取内容，格式不可改动
-->

**生成时间：** {{ timestamp }}
**Issue 追踪：** {{ issue_url }}
**复杂度评分：** {{ complexity_score }}/100 ({{ complexity_level }})
**测试层级：** Tier {{ test_tier }}

---

## 1. 应用概述

> 数据来源：step-01 Phase 1-6

| 项目 | 详情 |
|------|------|
| 名称 | {{ app_name }} |
| 商标名 | {{ trademark }} |
| 用途 | {{ app_description }} |
| 官方网站 | {{ official_url }} |
| 镜像 | {{ image_name }}:{{ version }} |
| 镜像来源 | {{ image_source_icon }} {{ image_source_type }} |
| Docker Hub | {{ dockerhub_url }} |
| 仓库地址 | {{ fork_url }} |
| 最低要求 | CPU {{ req_cpu }} 核 / 内存 {{ req_memory }}G / 磁盘 {{ req_disk }}G |

---

## 2. 容器架构设计

> 数据来源：step-02 Phase 2

### 2.0 架构决策依据

| 项目 | 内容 |
|------|------|
| 官方 Compose 类型 | {{ compose_type }} (A 产品级 / B Demo / C 最小化 / 无) |
{% if compose_type == 'B' %}
| ⚠️ Demo 架构 | 官方 compose 为演示用途 ({{ official_service_count }} 容器)，不适合直接改造 |
| 用户选择的方案 | {{ user_architecture_choice }} |
| 决策来源 | step-01 Phase 10g 用户确认 |
{% else %}
| 决策来源 | 官方 compose 直接改造 |
{% endif %}

### 2.1 服务拓扑

```
[用户] → :$W9_HTTP_PORT_SET → {{ main_service }}(:{{ internal_port }})
{% for dep in dependencies %}
                                ↳ → {{ dep.name }}(:{{ dep.port }})
{% endfor %}
```

### 2.2 服务列表

| 服务 | 镜像 | 容器名 | 端口 | 用途 |
|------|------|--------|------|------|
| {{ main_service }} (主) | $W9_REPO:$W9_VERSION | $W9_ID | $W9_HTTP_PORT_SET:{{ internal_port }} | {{ main_purpose }} |
{% for s in dep_services %}
| {{ s.name }} | {{ s.image }} | $W9_ID-{{ s.name }} | {{ s.port_mapping }} | {{ s.purpose }} |
{% endfor %}

**总计：** {{ total_containers }} 个容器

### 2.3 持久化卷

| 卷名 | 挂载路径 | 用途 |
|------|---------|------|
{% for v in named_volumes %}
| {{ v.name }} | {{ v.path }} | {{ v.purpose }} |
{% endfor %}
{% if not named_volumes %}

（无命名卷）
{% endif %}

---

## 3. W9_* 关键决策

> 数据来源：step-02 Phase 3b-3c

### 3.1 W9_LOGIN_USER / W9_LOGIN_PASSWORD

**决策：** {% if needs_login %}✅ 包含 — W9_LOGIN_USER={{ login_username }}{% else %}❌ 排除{% endif %}

| 项目 | 内容 |
|------|------|
| 证据 | {{ login_evidence }} |
| 置信度 | {{ login_confidence }}% |
{% if login_confidence < 85 %}
| ⚠️ 不确定性 | {{ login_uncertainty }} — 需测试验证 |
{% endif %}

### 3.2 W9_URL_REPLACE

**决策：** {% if needs_url_replace %}✅ 包含 — W9_URL_REPLACE=true{% else %}❌ 排除{% endif %}

| 项目 | 内容 |
|------|------|
{% if needs_url_replace %}
| 引用方式 | {{ url_usage }} |
| W9_URL 格式 | {{ url_format }} |
{% else %}
| 理由 | {{ no_url_replace_reason }} |
{% endif %}
| 置信度 | {{ url_confidence }}% |
{% if url_confidence < 85 %}
| ⚠️ 不确定性 | {{ url_uncertainty }} — 需测试验证 |
{% endif %}

### 3.3 附加 W9_* 变量

> 参考真实应用（如 wordpress）中使用的额外 W9_* 变量

| 变量 | 值 | 包含条件 | 本应用决策 |
|------|-----|---------|-----------|
| W9_ADMIN_PATH | {{ admin_path_value }} | 有独立管理后台路径 | {{ admin_path_decision }} |
| W9_DB_EXPOSE | {{ db_expose_value }} | 有数据库服务 | {{ db_expose_decision }} |
| W9_DB_VERSION | {{ db_version_value }} | 有数据库服务 | {{ db_version_decision }} |

{% if no_extra_w9_vars %}
（本应用无需附加 W9_* 变量）
{% endif %}

---

## 4. .env 文件预览 📌

> 数据来源：step-02 Phase 3e | step-03 Phase 3 直接使用此内容生成文件

```env
{{ env_preview }}
```

**变量统计：** {{ env_total_count }} 个（系统 {{ env_system_count }} + 应用特定 {{ env_app_specific_count }}）

---

## 5. docker-compose.yml 改造方案

> 数据来源：step-02 Phase 4

### 5.1 改造后 compose 📌

> step-03 Phase 4 直接使用此内容生成文件

```yaml
{{ transformed_compose }}
```

**官方参考来源：** {{ official_compose_source }}

### 5.2 改造清单 📌

> step-03 Notes.md 引用改造说明

| 序号 | 改造项 | 规则 | 说明 |
|------|--------|------|------|
{% for c in transformation_changes %}
| {{ loop.index }} | {{ c.what }} | {{ c.rule_type }} | {{ c.why }} |
{% endfor %}

> 规则类型：✅必须 = 7 项强制规范（镜像变量/容器命名/端口变量/外部网络/重启策略/env_file/密码统一）/ ⚠️可选 = 根据应用特性

---

## 6. src/ 文件规划 📌

> 数据来源：step-02 Phase 5 | step-03 Phase 5 直接使用此清单

### 6.1 配置文件映射

{% if src_files %}
| 文件 | 映射目标 | 内容来源 | 说明 |
|------|---------|---------|------|
{% for f in src_files %}
| src/{{ f.filename }} | {{ f.container_path }} | {{ f.source }} | {{ f.description }} |
{% endfor %}
| src/README.md | （不映射） | 自动生成 | 配置说明文档 |
{% else %}
无需配置文件映射。仅创建 src/README.md。
{% endif %}

### 6.2 数据持久化卷

{% for v in data_volumes %}
- **{{ v.name }}** → {{ v.path }}（{{ v.purpose }}）
{% endfor %}
{% if not data_volumes %}
（无数据持久化卷）
{% endif %}

---

## 7. 简化建议

{% if needs_simplification %}
> 复杂度 ≥ 70，提供精简方案

### 完整版（推荐）— {{ total_containers }} 容器

{% for s in all_services %}
- {{ s.name }} — {{ s.purpose }}
{% endfor %}

### 精简版（可选）— {{ simplified_containers }} 容器

| 服务 | 操作 | 原因 |
|------|------|------|
{% for s in core_services %}
| {{ s.name }} | ✅ 保留 | {{ s.purpose }} |
{% endfor %}
{% for s in removed_services %}
| {{ s.name }} | ❌ 移除 | {{ s.reason }} |
{% endfor %}

**功能限制：**
{% for l in limitations %}
- ⚠️ {{ l }}
{% endfor %}

{% else %}
不适用（复杂度 < 70，无需简化）
{% endif %}

---

## 8. 测试策略 📌

> 数据来源：step-02 Phase 6 | step-03 传递给 step-04

**复杂度等级：** Tier {{ test_tier }} — {{ test_tier_description }}

| 参数 | 值 |
|------|-----|
| 启动等待 | {{ estimated_startup_time }} 秒 |
| 部署超时 | {{ estimated_timeout }} 秒 |
| 期望响应码 | {{ expected_http_code }} |

### L1 静态验证（agent 自动，无网络）

- [ ] `docker compose config` 语法通过
- [ ] volume 映射的 src/ 文件全部存在
- [ ] .env / docker-compose.yml / variables.json 必需文件存在
- [ ] docker-compose.yml 引用的变量在 .env 中已定义

### L2 部署验证（agent SSH 远程执行）

- [ ] 容器启动: {{ total_containers }} 个服务全部 running
- [ ] HTTP 连通: `curl http://localhost:{{ '{' }}W9_HTTP_PORT_SET{{ '}' }}` 返回 {{ expected_http_code }}
{% for t in l2_test_items %}
- [ ] {{ t }}
{% endfor %}
- [ ] 日志无 FATAL/PANIC 级别错误

### L3 核心功能验证（人工浏览器执行）

{% for t in l3_test_items %}
- [ ] {{ t }}
{% endfor %}

### 特别注意

{% for p in key_test_points %}
- {{ p }}
{% endfor %}

---

## 9. 风险评估

> 数据来源：step-02 Phase 7a

| 等级 | 风险描述 | 影响 | 缓解方案 |
|------|---------|------|---------|
{% for r in risks %}
| {{ r.level }} | {{ r.description }} | {{ r.impact }} | {{ r.mitigation }} |
{% endfor %}

---

## 10. 开发文件清单 📌

> 数据来源：step-02 Phase 7b | step-03 Phase 2-7 按此顺序生成

| 序号 | 文件路径 | 类型 | 说明 |
|------|---------|------|------|
| 1 | apps/{{ app_name }}/ | 目录 | 应用根目录 |
| 2 | apps/{{ app_name }}/.env | 生成 | 环境变量（{{ env_total_count }} 个） |
| 3 | apps/{{ app_name }}/docker-compose.yml | 生成 | 编排文件（{{ total_containers }} 服务） |
| 4 | apps/{{ app_name }}/src/ | 目录 | 配置文件目录 |
{% for f in src_files %}
| {{ loop.index + 4 }} | apps/{{ app_name }}/src/{{ f.filename }} | 生成 | {{ f.description }} |
{% endfor %}
| {{ src_files_count + 5 }} | apps/{{ app_name }}/src/README.md | 生成 | 配置说明 |
| {{ src_files_count + 6 }} | apps/{{ app_name }}/variables.json | 生成 | README 模板变量 |
| {{ src_files_count + 7 }} | apps/{{ app_name }}/CHANGELOG.md | 生成 | 变更日志 |
| {{ src_files_count + 8 }} | apps/{{ app_name }}/Notes.md | 生成 | 开发备注 |

**总计：** {{ total_file_count }} 个文件

---

## 11. variables.json 预览

```json
{
  "name": "{{ app_name }}",
  "trademark": "{{ trademark }}",
  "release": true,
  "fork_url": "{{ fork_url }}",
  "version_from": "{{ version_from_url }}",
  "edition": [
    {
      "dist": "community",
      "version": ["{{ version }}", "latest"]
    }
  ],
  "requirements": {
    "cpu": "{{ req_cpu }}",
    "memory": "{{ req_memory }}",
    "disk": "{{ req_disk }}",
    "url": "{{ req_url }}"
  }
}
```

---

**状态：** 等待批准
**下一步：** 用户 review 后选择 [Y] 批准 / [M] 调整 / [N] 暂停
