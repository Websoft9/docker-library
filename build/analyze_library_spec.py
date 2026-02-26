#!/usr/bin/env python3
"""
Docker Library Specification Analyzer
扫描 apps/ 目录下所有应用，提取实际的规范模式和规则
"""

import os
import re
import json
import yaml
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Any

class LibraryAnalyzer:
    def __init__(self, apps_dir: str):
        self.apps_dir = Path(apps_dir)
        self.apps = []
        self.env_patterns = defaultdict(list)
        self.compose_patterns = defaultdict(list)
        self.variables_patterns = defaultdict(list)
        self.src_patterns = defaultdict(list)
        self.statistics = {
            'total_apps': 0,
            'has_env': 0,
            'has_compose': 0,
            'has_variables': 0,
            'has_src': 0,
            'env_vars': Counter(),
            'compose_features': Counter(),
        }
    
    def scan_all_apps(self):
        """扫描所有应用目录"""
        print(f"🔍 扫描 {self.apps_dir} 目录...")
        
        for app_path in sorted(self.apps_dir.iterdir()):
            if not app_path.is_dir():
                continue
            
            app_name = app_path.name
            self.statistics['total_apps'] += 1
            
            app_data = {
                'name': app_name,
                'path': str(app_path),
                'has_env': False,
                'has_compose': False,
                'has_variables': False,
                'has_src': False,
                'env_vars': {},
                'compose_data': None,
                'variables_data': None,
                'src_files': [],
            }
            
            # 分析 .env 文件
            env_file = app_path / '.env'
            if env_file.exists():
                app_data['has_env'] = True
                self.statistics['has_env'] += 1
                app_data['env_vars'] = self._analyze_env(env_file)
            
            # 分析 docker-compose.yml
            compose_file = app_path / 'docker-compose.yml'
            if compose_file.exists():
                app_data['has_compose'] = True
                self.statistics['has_compose'] += 1
                app_data['compose_data'] = self._analyze_compose(compose_file)
            
            # 分析 variables.json
            variables_file = app_path / 'variables.json'
            if variables_file.exists():
                app_data['has_variables'] = True
                self.statistics['has_variables'] += 1
                app_data['variables_data'] = self._analyze_variables(variables_file)
            
            # 分析 src/ 目录
            src_dir = app_path / 'src'
            if src_dir.exists() and src_dir.is_dir():
                app_data['has_src'] = True
                self.statistics['has_src'] += 1
                app_data['src_files'] = self._analyze_src(src_dir)
            
            self.apps.append(app_data)
        
        print(f"✅ 扫描完成: {self.statistics['total_apps']} 个应用")
    
    def _analyze_env(self, env_file: Path) -> Dict[str, Any]:
        """分析 .env 文件，提取变量模式"""
        vars_dict = {}
        content = env_file.read_text(encoding='utf-8', errors='ignore')
        
        # 提取所有环境变量
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key = line.split('=')[0].strip()
                value = line.split('=', 1)[1].strip() if len(line.split('=', 1)) > 1 else ''
                vars_dict[key] = value
                self.statistics['env_vars'][key] += 1
        
        return vars_dict
    
    def _analyze_compose(self, compose_file: Path) -> Dict[str, Any]:
        """分析 docker-compose.yml 文件"""
        try:
            with open(compose_file, 'r', encoding='utf-8') as f:
                compose_data = yaml.safe_load(f)
            
            if not compose_data:
                return {}
            
            features = {
                'services_count': len(compose_data.get('services', {})),
                'has_networks': 'networks' in compose_data,
                'has_volumes': 'volumes' in compose_data,
                'services': list(compose_data.get('services', {}).keys()),
                'volume_mappings': [],
                'uses_external_network': False,
            }
            
            # 检查网络配置
            if 'networks' in compose_data:
                for net_name, net_config in compose_data['networks'].items():
                    if isinstance(net_config, dict) and net_config.get('external'):
                        features['uses_external_network'] = True
                        self.statistics['compose_features']['external_network'] += 1
            
            # 提取卷映射模式
            for service_name, service_config in compose_data.get('services', {}).items():
                if 'volumes' in service_config:
                    for vol in service_config['volumes']:
                        if isinstance(vol, str) and './src/' in vol:
                            features['volume_mappings'].append(vol)
                            self.statistics['compose_features']['src_volume_mapping'] += 1
            
            return features
            
        except Exception as e:
            print(f"⚠️  解析 {compose_file} 失败: {e}")
            return {}
    
    def _analyze_variables(self, variables_file: Path) -> Dict[str, Any]:
        """分析 variables.json 文件"""
        try:
            with open(variables_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  解析 {variables_file} 失败: {e}")
            return {}
    
    def _analyze_src(self, src_dir: Path) -> List[str]:
        """分析 src/ 目录结构"""
        files = []
        for item in src_dir.rglob('*'):
            if item.is_file():
                rel_path = item.relative_to(src_dir)
                files.append(str(rel_path))
        return files
    
    def analyze_w9_patterns(self) -> Dict[str, Any]:
        """分析 W9_* 变量使用模式"""
        print("\n📊 分析 W9_* 变量模式...")
        
        w9_vars = {k: v for k, v in self.statistics['env_vars'].items() if k.startswith('W9_')}
        
        # 分析条件变量模式
        has_login_user = []
        has_login_password = []
        has_url_replace = []
        has_url = []
        
        for app in self.apps:
            app_name = app['name']
            env_vars = app['env_vars']
            
            if 'W9_LOGIN_USER' in env_vars:
                has_login_user.append(app_name)
            if 'W9_LOGIN_PASSWORD' in env_vars:
                has_login_password.append(app_name)
            if 'W9_URL_REPLACE' in env_vars:
                has_url_replace.append(app_name)
            if 'W9_URL' in env_vars:
                has_url.append(app_name)
        
        return {
            'all_w9_vars': dict(w9_vars),
            'login_credentials': {
                'count': len(has_login_user),
                'apps': has_login_user[:10],  # 只显示前10个
            },
            'url_replace': {
                'count': len(has_url_replace),
                'apps': has_url_replace[:10],
            },
            'url_defined': {
                'count': len(has_url),
                'apps': has_url[:10],
            }
        }
    
    def analyze_compose_patterns(self) -> Dict[str, Any]:
        """分析 docker-compose.yml 模式"""
        print("\n📊 分析 docker-compose.yml 模式...")
        
        service_counts = []
        external_network_apps = []
        src_mapping_apps = []
        
        for app in self.apps:
            if app['compose_data']:
                service_counts.append(app['compose_data'].get('services_count', 0))
                
                if app['compose_data'].get('uses_external_network'):
                    external_network_apps.append(app['name'])
                
                if app['compose_data'].get('volume_mappings'):
                    src_mapping_apps.append({
                        'name': app['name'],
                        'mappings': app['compose_data']['volume_mappings']
                    })
        
        return {
            'service_distribution': {
                'min': min(service_counts) if service_counts else 0,
                'max': max(service_counts) if service_counts else 0,
                'avg': sum(service_counts) / len(service_counts) if service_counts else 0,
            },
            'external_network': {
                'count': len(external_network_apps),
                'percentage': len(external_network_apps) / self.statistics['total_apps'] * 100,
            },
            'src_mappings': {
                'count': len(src_mapping_apps),
                'examples': src_mapping_apps[:5],
            }
        }
    
    def extract_rules(self) -> Dict[str, Any]:
        """提取实际的规范规则"""
        print("\n📝 提取规范规则...")
        
        rules = {
            'env_file_rules': self._extract_env_rules(),
            'compose_rules': self._extract_compose_rules(),
            'src_directory_rules': self._extract_src_rules(),
            'variables_json_rules': self._extract_variables_rules(),
        }
        
        return rules
    
    def _extract_env_rules(self) -> Dict[str, Any]:
        """提取 .env 文件规则"""
        # 统计必需的 W9_ 变量
        required_vars = {}
        optional_vars = {}
        
        total_apps = self.statistics['has_env']
        
        for var, count in self.statistics['env_vars'].items():
            if not var.startswith('W9_'):
                continue
            
            percentage = (count / total_apps * 100) if total_apps > 0 else 0
            
            if percentage > 95:  # 超过95%的应用都有
                required_vars[var] = {
                    'count': count,
                    'percentage': percentage,
                    'status': 'required'
                }
            elif percentage > 50:  # 50-95%
                optional_vars[var] = {
                    'count': count,
                    'percentage': percentage,
                    'status': 'common'
                }
        
        return {
            'required_w9_vars': required_vars,
            'optional_w9_vars': optional_vars,
            'conditional_vars': {
                'W9_LOGIN_USER': '仅当应用有内置用户认证时包含',
                'W9_LOGIN_PASSWORD': '仅当应用有内置用户认证时包含',
                'W9_URL_REPLACE': '仅当 W9_URL 在 docker-compose.yml 中被实际使用时包含',
            }
        }
    
    def _extract_compose_rules(self) -> Dict[str, Any]:
        """提取 docker-compose.yml 规则"""
        return {
            'network_requirement': 'websoft9 external network (必需)',
            'container_naming': '使用 $W9_ID 或 $W9_ID-servicename 模式',
            'restart_policy': 'unless-stopped (推荐)',
            'external_network_usage': f"{self.statistics['compose_features']['external_network']} 个应用使用外部网络",
        }
    
    def _extract_src_rules(self) -> Dict[str, Any]:
        """提取 src/ 目录规则"""
        apps_with_src = sum(1 for app in self.apps if app['has_src'])
        
        return {
            'usage': f"{apps_with_src} / {self.statistics['total_apps']} 应用使用 src/ 目录",
            'purpose': '存储需要映射到容器的配置文件',
            'requirement': '所有 docker-compose.yml 中引用的 ./src/ 文件必须实际存在',
            'best_practice': '包含 src/README.md 说明各文件用途',
        }
    
    def _extract_variables_rules(self) -> Dict[str, Any]:
        """提取 variables.json 规则"""
        # 分析 variables.json 的常见字段
        all_keys = set()
        for app in self.apps:
            if app['variables_data']:
                all_keys.update(app['variables_data'].keys())
        
        return {
            'purpose': '为 README 模板提供变量',
            'common_fields': sorted(list(all_keys)),
        }
    
    def generate_report(self) -> str:
        """生成分析报告"""
        print("\n📄 生成规范文档...")
        
        w9_patterns = self.analyze_w9_patterns()
        compose_patterns = self.analyze_compose_patterns()
        rules = self.extract_rules()
        
        report = f"""# Docker Library 规范文档
*自动生成于扫描 {self.statistics['total_apps']} 个应用*

---

## 1. 项目概述

### 1.1 基本信息
- **应用总数**: {self.statistics['total_apps']}
- **包含 .env**: {self.statistics['has_env']} ({self.statistics['has_env']/self.statistics['total_apps']*100:.1f}%)
- **包含 docker-compose.yml**: {self.statistics['has_compose']} ({self.statistics['has_compose']/self.statistics['total_apps']*100:.1f}%)
- **包含 variables.json**: {self.statistics['has_variables']} ({self.statistics['has_variables']/self.statistics['total_apps']*100:.1f}%)
- **包含 src/ 目录**: {self.statistics['has_src']} ({self.statistics['has_src']/self.statistics['total_apps']*100:.1f}%)

### 1.2 标准化模式
所有应用遵循统一的目录结构：
```
apps/{{{{app_name}}}}/
├── .env                  # 环境变量配置
├── docker-compose.yml    # Docker Compose 编排文件
├── variables.json        # README 模板变量
├── README.md            # 自动生成的文档
├── Notes.md             # 开发备注
└── src/                 # 自定义配置文件（可选）
```

---

## 2. .env 文件规范

### 2.1 必需的 W9_* 变量

基于扫描发现，以下变量在 >95% 的应用中存在，视为**必需变量**：

"""
        
        # 必需变量列表
        required = rules['env_file_rules']['required_w9_vars']
        for var, info in sorted(required.items()):
            report += f"- **{var}**: 出现在 {info['count']}/{self.statistics['has_env']} 应用 ({info['percentage']:.1f}%)\n"
        
        report += f"""

### 2.2 条件变量（Conditional Variables）

以下变量**不是**在所有应用中都需要，需根据应用特性判断：

#### W9_LOGIN_USER 和 W9_LOGIN_PASSWORD
- **出现频率**: {w9_patterns['login_credentials']['count']}/{self.statistics['total_apps']} 应用 ({w9_patterns['login_credentials']['count']/self.statistics['total_apps']*100:.1f}%)
- **包含条件**: ✅ 仅当应用有内置的用户认证系统
- **排除情况**: ❌ 无认证系统（如 nginx）、仅 token 认证、数据库服务

**示例应用（包含登录凭证）**: {', '.join(w9_patterns['login_credentials']['apps'][:5])}

#### W9_URL_REPLACE
- **出现频率**: {w9_patterns['url_replace']['count']}/{self.statistics['total_apps']} 应用 ({w9_patterns['url_replace']['count']/self.statistics['total_apps']*100:.1f}%)
- **包含条件**: ✅ 仅当 W9_URL 在 docker-compose.yml 中被实际引用
- **排除情况**: ❌ W9_URL 存在但未被使用

**示例应用（使用 URL 替换）**: {', '.join(w9_patterns['url_replace']['apps'][:5])}

#### W9_URL
- **出现频率**: {w9_patterns['url_defined']['count']}/{self.statistics['total_apps']} 应用 ({w9_patterns['url_defined']['count']/self.statistics['total_apps']*100:.1f}%)
- **标准格式**: `W9_URL=internet_ip:$W9_HTTP_PORT_SET` 或 `W9_URL=appname.example.com`
- **用途**: 提供应用外部访问 URL 占位符

### 2.3 .env 文件结构模板

```bash
# 版本和仓库信息
W9_REPO={{{{official_image_name}}}}
W9_VERSION={{{{version}}}}
W9_POWER_PASSWORD={{{{generated_password}}}}

# 用户可配置的设置
W9_HTTP_PORT_SET='9001'

#### --  Not allowed to edit below environments when recreate app based on existing data  -- ####
W9_ID='{{{{app_name}}}}'
W9_HTTP_PORT=80
W9_NETWORK=websoft9

# 条件变量 - 根据应用特性包含
# W9_LOGIN_USER=admin                    # 仅当有内置认证
# W9_LOGIN_PASSWORD=$W9_POWER_PASSWORD   # 仅当有内置认证
# W9_URL=internet_ip:$W9_HTTP_PORT_SET   # 根据需要
# W9_URL_REPLACE=true                    # 仅当 W9_URL 被实际使用
#### -------------------------------------------------------------------------------------- ####

# 应用特定的环境变量
{{{{APP_SPECIFIC_VARS}}}}
```

---

## 3. docker-compose.yml 规范

### 3.1 网络配置

基于扫描：**{compose_patterns['external_network']['percentage']:.1f}%** 的应用使用外部网络。

**标准网络配置**（必需）：
```yaml
networks:
  default:
    name: ${{W9_NETWORK}}
    external: true
```

**关键要求**:
- 所有应用必须使用 `websoft9` 外部网络
- 网络必须在应用部署前手动创建: `docker network create websoft9`

### 3.2 容器命名规范

**模式**: `$W9_ID` 或 `$W9_ID-{{{{service_name}}}}`

示例：
```yaml
services:
  app:
    container_name: $W9_ID
    # ...
  
  database:
    container_name: $W9_ID-mysql
    # ...
```

### 3.3 服务配置

**统计数据**:
- 最少服务数: {compose_patterns['service_distribution']['min']:.0f}
- 最多服务数: {compose_patterns['service_distribution']['max']:.0f}
- 平均服务数: {compose_patterns['service_distribution']['avg']:.1f}

**推荐配置**:
```yaml
services:
  app:
    container_name: $W9_ID
    image: ${{W9_REPO}}:${{W9_VERSION}}
    restart: unless-stopped
    ports:
      - "${{W9_HTTP_PORT_SET}}:${{W9_HTTP_PORT}}"
    environment:
      # 应用环境变量
    volumes:
      - ./src/config.conf:/app/config.conf  # 配置文件映射
      - app_data:/app/data                  # 数据持久化
    networks:
      - default
```

### 3.4 卷映射规范

**基于扫描发现**: {compose_patterns['src_mappings']['count']} 个应用使用 `./src/` 卷映射

**关键规则**:
- ✅ 所有引用 `./src/*` 的文件必须实际存在于 `apps/{{{{app_name}}}}/src/` 目录
- ✅ 配置文件应包含合理的默认值
- ❌ 不能引用不存在的文件

**示例映射**:
"""
        
        # 添加实际的映射示例
        if compose_patterns['src_mappings']['examples']:
            for example in compose_patterns['src_mappings']['examples'][:3]:
                report += f"\n**{example['name']}**:\n"
                for mapping in example['mappings'][:3]:
                    report += f"- `{mapping}`\n"
        
        report += f"""

---

## 4. src/ 目录规范

### 4.1 使用统计
- **使用 src/ 的应用**: {rules['src_directory_rules']['usage']}
- **用途**: {rules['src_directory_rules']['purpose']}

### 4.2 关键要求

1. **文件存在性验证**
   - docker-compose.yml 中的所有 `./src/*` 引用必须对应实际文件
   - 使用此命令验证:
   ```bash
   for vol in $(grep "./src/" docker-compose.yml | cut -d: -f1 | tr -d ' -'); do
     [ -f "$vol" ] || echo "Missing: $vol"
   done
   ```

2. **配置文件质量**
   - 包含合理的默认配置
   - 添加注释说明关键参数
   - 创建 `src/README.md` 说明各文件用途

3. **最佳实践**
   - 提供开箱即用的配置
   - 避免需要手动编辑才能启动
   - 在 Notes.md 中记录定制化建议

---

## 5. variables.json 规范

### 5.1 用途
为 Jinja2 模板生成 README.md 提供元数据

### 5.2 常见字段
基于扫描发现的常用字段：
"""
        
        for field in sorted(rules['variables_json_rules']['common_fields'])[:15]:
            report += f"- `{field}`\n"
        
        report += f"""

### 5.3 示例结构
```json
{{
  "name": "WordPress",
  "version": "6.9",
  "description": "Open source CMS platform",
  "port": "9001",
  "category": "CMS",
  "tags": ["blog", "cms", "php"],
  "official_website": "https://wordpress.org",
  "official_docs": "https://wordpress.org/documentation/",
  "developer": "WordPress Foundation"
}}
```

---

## 6. 条件逻辑决策树

### 6.1 W9_LOGIN_USER/PASSWORD 决策

```
应用是否有用户管理系统？
├─ 是 → 是否支持通过环境变量预配置管理员？
│  ├─ 是 → ✅ 包含 W9_LOGIN_USER 和 W9_LOGIN_PASSWORD
│  └─ 否 → ❌ 不包含（用户需手动创建）
└─ 否 → ❌ 不包含
```

**包含示例**: WordPress, GitLab, Odoo, Joomla
**排除示例**: Nginx, Apache, HuggingChat, 数据库服务

### 6.2 W9_URL_REPLACE 决策

```
W9_URL 是否在 docker-compose.yml 或应用配置中被引用？
├─ 是 → ✅ 包含 W9_URL_REPLACE=true
└─ 否 → ❌ 不包含 W9_URL_REPLACE（但保留 W9_URL）
```

**包含示例**: Nextcloud (TRUSTED_DOMAINS), GitLab (external_url)
**排除示例**: 仅定义但未使用 W9_URL 的应用

---

## 7. 验证清单

### 7.1 .env 文件验证
- [ ] 包含所有必需的 W9_* 变量
- [ ] W9_LOGIN_* 仅在有内置认证时包含
- [ ] W9_URL_REPLACE 仅在 W9_URL 被使用时包含
- [ ] 密码使用 $W9_POWER_PASSWORD 统一管理

### 7.2 docker-compose.yml 验证
- [ ] 使用 websoft9 外部网络
- [ ] 容器名遵循 $W9_ID 模式
- [ ] restart: unless-stopped
- [ ] 所有 ./src/ 映射的文件都存在

### 7.3 src/ 目录验证
- [ ] 所有引用的配置文件已创建
- [ ] 配置文件包含合理默认值
- [ ] 存在 src/README.md 说明文档

### 7.4 整体验证命令

```bash
# 检查 1: 验证登录凭证是否必要
grep -q "W9_LOGIN_USER" .env && echo "检查应用是否有内置认证"

# 检查 2: 验证 W9_URL 是否被使用
grep "\$W9_URL" docker-compose.yml || echo "W9_URL 未使用，移除 W9_URL_REPLACE"

# 检查 3: 验证所有 src/ 文件存在
for vol in $(grep "./src/" docker-compose.yml | cut -d: -f1 | tr -d ' -'); do
  [ -f "$vol" ] || echo "缺失文件: $vol"
done

# 检查 4: 测试部署
docker compose up -d
sleep 30
curl -I http://localhost:9001
docker compose down -v
```

---

## 8. 常见模式总结

### 8.1 W9_* 变量使用频率

| 变量名 | 出现次数 | 使用率 | 状态 |
|--------|---------|--------|------|
"""
        
        # 添加变量统计表
        for var, count in sorted(w9_patterns['all_w9_vars'].items(), key=lambda x: x[1], reverse=True)[:15]:
            percentage = count / self.statistics['total_apps'] * 100
            status = "必需" if percentage > 95 else ("常用" if percentage > 50 else "条件")
            report += f"| {var} | {count} | {percentage:.1f}% | {status} |\n"
        
        report += f"""

### 8.2 应用复杂度分布

- **简单应用** (1 服务): Web 服务器、工具类
- **标准应用** (2-3 服务): 应用 + 数据库组合
- **复杂应用** (4+ 服务): 企业级应用、微服务架构

### 8.3 最佳实践原则

1. **官方优先**: 以官方 docker-compose.yml 为基准，仅添加标准化配置
2. **文档驱动**: 先生成开发计划，再编写代码
3. **条件包含**: 仅在实际需要时包含可选变量
4. **验证完整**: 确保所有引用的文件都存在
5. **测试优先**: 部署测试通过后才提交

---

## 9. 规范来源

本规范文档通过以下方式生成：

1. **扫描范围**: {self.statistics['total_apps']} 个应用
2. **分析维度**: 
   - .env 文件模式（{self.statistics['has_env']} 个样本）
   - docker-compose.yml 结构（{self.statistics['has_compose']} 个样本）
   - variables.json 字段（{self.statistics['has_variables']} 个样本）
   - src/ 目录使用（{self.statistics['has_src']} 个样本）

3. **统计方法**: 
   - 必需变量: 出现率 > 95%
   - 常用变量: 出现率 > 50%
   - 条件变量: 根据实际使用场景判断

4. **生成工具**: `build/analyze_library_spec.py`

---

*本文档反映了 Docker Library 项目的实际规范，基于真实应用扫描生成，持续更新。*
"""
        
        return report


def main():
    """主函数"""
    import sys
    
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    apps_dir = project_root / 'apps'
    
    if not apps_dir.exists():
        print(f"❌ 错误: apps/ 目录不存在: {apps_dir}")
        sys.exit(1)
    
    # 创建分析器
    analyzer = LibraryAnalyzer(apps_dir)
    
    # 扫描所有应用
    analyzer.scan_all_apps()
    
    # 生成报告
    report = analyzer.generate_report()
    
    # 保存报告
    output_dir = project_root / '_bmad-output'
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'docker-library-spec.md'
    output_file.write_text(report, encoding='utf-8')
    
    print(f"\n✅ 规范文档已生成: {output_file}")
    print(f"📊 扫描统计:")
    print(f"   - 总应用数: {analyzer.statistics['total_apps']}")
    print(f"   - W9_* 变量数: {len([k for k in analyzer.statistics['env_vars'].keys() if k.startswith('W9_')])}")
    print(f"   - 使用 src/ 的应用: {analyzer.statistics['has_src']}")


if __name__ == '__main__':
    main()
