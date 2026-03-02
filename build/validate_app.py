#!/usr/bin/env python3
"""
validate_app.py — Docker Library 应用规范校验脚本

用法:
  python3 build/validate_app.py "wordpress"
  python3 build/validate_app.py "wordpress,nginx,gitlab"
  python3 build/validate_app.py "ALL"
  python3 build/validate_app.py "wordpress" --output-json /tmp/result.json --pr-comment /tmp/comment.md

退出码: 0=全通过  1=有FAIL  2=脚本错误
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# ───────────────────────── 检查函数 ─────────────────────────

def check_required_files(app_dir: Path) -> dict:
    """三件套文件存在检查"""
    missing = [f for f in [".env", "docker-compose.yml", "variables.json"]
               if not (app_dir / f).exists()]
    if missing:
        return fail(f"缺少文件: {', '.join(missing)}")
    return ok("三件套齐全")


def check_compose_syntax(app_dir: Path) -> dict:
    """docker compose config 语法合法"""
    result = subprocess.run(
        ["docker", "compose", "-f", str(app_dir / "docker-compose.yml"),
         "--env-file", str(app_dir / ".env"), "config", "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return fail(f"compose 语法错误: {result.stderr.strip()[:200]}")
    return ok("语法合法")


def check_required_env_fields(app_dir: Path) -> dict:
    """W9_REPO / W9_VERSION / W9_HTTP_PORT_SET 存在"""
    env_content = _read_env(app_dir)
    missing = [k for k in ["W9_REPO", "W9_VERSION", "W9_HTTP_PORT_SET"]
               if k not in env_content]
    if missing:
        return fail(f"缺少必要字段: {', '.join(missing)}")
    return ok("必要字段齐全")


def check_no_latest_version(app_dir: Path) -> dict:
    """W9_VERSION 不为 latest"""
    env_content = _read_env(app_dir)
    version = env_content.get("W9_VERSION", "")
    if version.strip().lower() == "latest":
        return fail("W9_VERSION=latest，必须指定明确版本号")
    if not version:
        return fail("W9_VERSION 为空")
    return ok(f"W9_VERSION={version}")


def check_restart_policy(app_dir: Path) -> dict:
    """所有 service 含 restart: unless-stopped"""
    content = _read_compose(app_dir)
    services = _extract_services(content)
    if not services:
        return ok("无 service（跳过）")
    missing = []
    for service in services:
        # 检查每个 service 块中是否包含 restart: unless-stopped
        if not re.search(r'restart:\s*unless-stopped', service):
            # 提取 service 名称
            name_match = re.match(r'\s{2,4}(\w[\w-]*):', service)
            name = name_match.group(1) if name_match else "unknown"
            missing.append(name)
    if missing:
        return fail(f"以下 service 缺少 restart: unless-stopped: {', '.join(missing)}")
    return ok("所有 service 已设置 restart: unless-stopped")


def check_container_naming(app_dir: Path) -> dict:
    """container_name 含 $W9_ID"""
    content = _read_compose(app_dir)
    # 找到所有 container_name
    names = re.findall(r'container_name:\s*(.+)', content)
    if not names:
        return fail("未找到 container_name（所有 service 都必须显式命名）")
    bad = [n.strip() for n in names if "$W9_ID" not in n and "${W9_ID}" not in n]
    if bad:
        return fail(f"container_name 未包含 $W9_ID: {', '.join(bad)}")
    return ok("container_name 均含 $W9_ID")


def check_network_config(app_dir: Path) -> dict:
    """使用 websoft9 外部网络且声明 external: true
    支持两种写法：
      - 直接写 websoft9（旧写法）
      - name: ${W9_NETWORK}（推荐，通过 .env 中 W9_NETWORK=websoft9 定义）
    """
    content = _read_compose(app_dir)
    env_content = _read_env(app_dir)
    if not re.search(r'external:\s*true', content):
        return fail("网络未声明 external: true")
    # 方式A: compose 中直接出现 websoft9
    uses_websoft9_literal = "websoft9" in content
    # 方式B: 使用 ${W9_NETWORK} 变量，且 .env 中 W9_NETWORK=websoft9
    uses_w9_network_var = bool(re.search(r'\$\{?W9_NETWORK\}?', content))
    w9_network_value = env_content.get("W9_NETWORK", "").strip()
    if uses_websoft9_literal or (uses_w9_network_var and w9_network_value == "websoft9"):
        return ok("websoft9 外部网络声明正确")
    return fail("未能确认使用 websoft9 网络（检查 W9_NETWORK 或网络名称）")


def check_src_files_exist(app_dir: Path) -> dict:
    """volumes 中 ./src/* 引用的文件均存在"""
    content = _read_compose(app_dir)
    src_refs = re.findall(r'[-\s]+(\.\/src\/[^\s:]+)', content)
    if not src_refs:
        return ok("无 src/ 文件映射")
    missing_files = []
    for ref in src_refs:
        # ./src/foo.conf → app_dir/src/foo.conf
        rel = ref.lstrip("./")
        full = app_dir / rel
        if not full.exists():
            missing_files.append(ref)
    if missing_files:
        return fail(f"src/ 引用文件不存在: {', '.join(missing_files)}")
    return ok(f"所有 {len(src_refs)} 个 src/ 文件映射均存在")


def check_url_replace_consistency(app_dir: Path) -> dict:
    """W9_URL_REPLACE 与 compose 引用 $W9_URL 一致"""
    env_content = _read_env(app_dir)
    compose_content = _read_compose(app_dir)
    has_replace_flag = env_content.get("W9_URL_REPLACE", "").strip().lower() == "true"
    has_url_in_compose = bool(re.search(r'\$W9_URL|\${W9_URL}', compose_content))
    if has_url_in_compose and not has_replace_flag:
        return fail("compose 中使用了 $W9_URL，但 .env 缺少 W9_URL_REPLACE=true")
    if has_replace_flag and not has_url_in_compose:
        return fail(".env 设置了 W9_URL_REPLACE=true，但 compose 中未使用 $W9_URL")
    return ok("W9_URL_REPLACE 配置一致")


def check_no_latest_image_tag(app_dir: Path) -> dict:
    """compose 中无硬编码 :latest（WARN）"""
    content = _read_compose(app_dir)
    # 排除注释行，查找 :latest
    lines = [l for l in content.splitlines() if not l.strip().startswith("#")]
    hits = [l.strip() for l in lines if re.search(r'image:.*:latest', l)]
    if hits:
        return warn(f"发现硬编码 :latest: {hits[0]}")
    return ok("无硬编码 :latest")


def check_no_privileged(app_dir: Path) -> dict:
    """无 privileged: true（WARN）"""
    content = _read_compose(app_dir)
    if re.search(r'privileged:\s*true', content):
        return warn("发现 privileged: true，请确认是否必要")
    return ok("无 privileged 模式")


# ───────────────────────── 辅助函数 ─────────────────────────

def ok(message: str) -> dict:
    return {"status": "PASS", "message": message}

def fail(message: str) -> dict:
    return {"status": "FAIL", "message": message}

def warn(message: str) -> dict:
    return {"status": "WARN", "message": message}

_env_cache: dict = {}
_compose_cache: dict = {}

def _read_env(app_dir: Path) -> dict:
    key = str(app_dir)
    if key not in _env_cache:
        env_file = app_dir / ".env"
        result = {}
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, _, v = line.partition("=")
                    result[k.strip()] = v.strip()
        _env_cache[key] = result
    return _env_cache[key]

def _read_compose(app_dir: Path) -> str:
    key = str(app_dir)
    if key not in _compose_cache:
        f = app_dir / "docker-compose.yml"
        _compose_cache[key] = f.read_text(encoding="utf-8") if f.exists() else ""
    return _compose_cache[key]

def _extract_services(compose_content: str) -> list:
    """粗略提取每个 service 的文本块，用于逐 service 检查"""
    # 找到 services: 块
    match = re.search(r'^services:\s*\n(.*?)(?=^\w|\Z)', compose_content,
                      re.MULTILINE | re.DOTALL)
    if not match:
        return []
    services_block = match.group(1)
    # 按顶层 service 分割（两空格缩进的 key）
    parts = re.split(r'(?=^  \w[\w-]*:)', services_block, flags=re.MULTILINE)
    return [p for p in parts if p.strip()]


# ───────────────────────── 核心校验 ─────────────────────────

ALL_CHECKS = [
    ("required_files",          "三件套文件存在",                         check_required_files),
    ("compose_syntax",          "compose 语法合法",                       check_compose_syntax),
    ("required_env_fields",     "W9_REPO/W9_VERSION/W9_HTTP_PORT_SET 存在", check_required_env_fields),
    ("no_latest_version",       "W9_VERSION 不为 latest",                 check_no_latest_version),
    ("restart_policy",          "所有 service 含 restart: unless-stopped", check_restart_policy),
    ("container_naming",        "container_name 含 $W9_ID",               check_container_naming),
    ("network_config",          "使用 websoft9 外部网络",                  check_network_config),
    ("src_files_exist",         "src/ 引用文件均存在",                     check_src_files_exist),
    ("url_replace_consistency", "W9_URL_REPLACE 配置一致",                 check_url_replace_consistency),
    ("no_latest_image_tag",     "无硬编码 :latest",                       check_no_latest_image_tag),
    ("no_privileged",           "无 privileged 模式",                     check_no_privileged),
]

# compose_syntax 依赖 Docker daemon，某些环境可能不可用时的降级处理
SKIP_IF_NO_DOCKER = {"compose_syntax"}


def validate_app(app_name: str, base_dir: Path) -> dict:
    app_dir = base_dir / "apps" / app_name
    if not app_dir.is_dir():
        return {
            "app": app_name,
            "passed": 0, "failed": 1, "warned": 0,
            "checks": [{"id": "app_exists", "description": "应用目录存在",
                        "status": "FAIL", "message": f"目录不存在: {app_dir}"}]
        }

    checks_result = []
    passed = failed = warned = 0

    for check_id, description, check_fn in ALL_CHECKS:
        try:
            r = check_fn(app_dir)
        except Exception as e:
            r = fail(f"检查异常: {e}")
        r["id"] = check_id
        r["description"] = description
        if r["status"] == "PASS":
            passed += 1
        elif r["status"] == "FAIL":
            failed += 1
        else:
            warned += 1
        checks_result.append(r)

    return {
        "app": app_name,
        "passed": passed,
        "failed": failed,
        "warned": warned,
        "checks": checks_result,
    }


# ───────────────────────── 报告生成 ─────────────────────────

def build_pr_comment(results: list) -> str:
    total = len(results)
    any_fail = any(r["failed"] > 0 for r in results)
    overall = "❌ 存在 FAIL 项，请修复后重新提交" if any_fail else "✅ 全部通过"

    lines = [
        "## 🤖 Static Validation Report",
        "",
        f"| 检查的应用数 | 总体结果 |",
        f"|---|---|",
        f"| {total} | {overall} |",
        "",
    ]

    for r in results:
        icon = "❌" if r["failed"] > 0 else ("⚠️" if r["warned"] > 0 else "✅")
        lines.append(f"### {icon} `{r['app']}`")
        lines.append("")
        lines.append("| 检查项 | 结果 | 说明 |")
        lines.append("|--------|------|------|")
        for c in r["checks"]:
            status_icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️"}.get(c["status"], "")
            lines.append(f"| {c['description']} | {status_icon} | {c['message']} |")
        lines.append("")

    return "\n".join(lines)


def print_summary(results: list) -> None:
    for r in results:
        status = "PASS" if r["failed"] == 0 else "FAIL"
        print(f"\n{'='*60}")
        print(f"  App: {r['app']}  [{status}]  "
              f"passed={r['passed']} failed={r['failed']} warned={r['warned']}")
        print(f"{'='*60}")
        for c in r["checks"]:
            icon = {"PASS": "✓", "FAIL": "✗", "WARN": "!"}.get(c["status"], " ")
            print(f"  [{icon}] {c['id']:<30}  {c['message']}")


# ───────────────────────── 入口 ─────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Docker Library 应用规范校验")
    parser.add_argument("apps", help="应用名称，逗号分隔，或 ALL")
    parser.add_argument("--output-json", help="JSON 结果输出路径")
    parser.add_argument("--pr-comment", help="PR 评论 Markdown 输出路径")
    parser.add_argument("--base-dir", default=".", help="仓库根目录（默认当前目录）")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    apps_root = base_dir / "apps"

    # 解析 app 列表
    if args.apps.strip().upper() == "ALL":
        app_names = sorted([d.name for d in apps_root.iterdir() if d.is_dir()])
    else:
        app_names = [a.strip() for a in args.apps.split(",") if a.strip()]

    if not app_names:
        print("ERROR: 未找到任何应用", file=sys.stderr)
        sys.exit(2)

    # 执行校验
    results = [validate_app(name, base_dir) for name in app_names]

    # 控制台输出
    print_summary(results)

    # 汇总
    total_failed = sum(r["failed"] for r in results)
    total_warned = sum(r["warned"] for r in results)
    apps_failed = sum(1 for r in results if r["failed"] > 0)

    print(f"\n{'='*60}")
    print(f"  总计: {len(results)} 个应用  {apps_failed} 个有 FAIL  "
          f"warned={total_warned}")
    print(f"{'='*60}\n")

    # JSON 输出
    output = {
        "summary": {
            "total": len(results),
            "apps_failed": apps_failed,
            "total_failed_checks": total_failed,
            "total_warned_checks": total_warned,
        },
        "apps": results,
    }

    if args.output_json:
        Path(args.output_json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"JSON 结果已写入: {args.output_json}")

    # PR 评论 Markdown 输出
    if args.pr_comment:
        comment = build_pr_comment(results)
        Path(args.pr_comment).parent.mkdir(parents=True, exist_ok=True)
        with open(args.pr_comment, "w", encoding="utf-8") as f:
            f.write(comment)
        print(f"PR 评论已写入: {args.pr_comment}")

    sys.exit(1 if apps_failed > 0 else 0)


if __name__ == "__main__":
    main()
