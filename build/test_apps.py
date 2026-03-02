#!/usr/bin/env python3
"""
test_apps.py — Docker Library 冒烟部署测试

用法:
  python3 build/test_apps.py "wordpress"
  python3 build/test_apps.py "wordpress,nginx"
  APP_LISTS="wordpress,nginx" python3 build/test_apps.py

退出码: 0=全通过  1=有失败  2=脚本错误
"""

import os
import sys
import time
import subprocess
from pathlib import Path

try:
    import requests
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: 缺少依赖，请运行: pip install requests python-dotenv", file=sys.stderr)
    sys.exit(2)

# ─── 配置 ───────────────────────────────────────────────────
MAX_WAIT_SECONDS = int(os.getenv("MAX_WAIT_SECONDS", "120"))
POLL_INTERVAL    = 10
SUCCESS_CODES    = {200, 301, 302, 303, 307, 308}
LOG_DIR          = Path("/tmp/docker-logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ─── 辅助函数 ────────────────────────────────────────────────

def compose_up(app_dir: Path) -> bool:
    result = subprocess.run(
        ["docker", "compose", "-f", str(app_dir / "docker-compose.yml"),
         "--env-file", str(app_dir / ".env"), "up", "-d"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"  [ERROR] docker compose up 失败:\n{result.stderr[:500]}")
    return result.returncode == 0


def compose_down(app_dir: Path):
    subprocess.run(
        ["docker", "compose", "-f", str(app_dir / "docker-compose.yml"),
         "--env-file", str(app_dir / ".env"), "down", "-v"],
        capture_output=True
    )


def save_logs(app_name: str, app_dir: Path):
    result = subprocess.run(
        ["docker", "compose", "-f", str(app_dir / "docker-compose.yml"),
         "--env-file", str(app_dir / ".env"), "logs", "--no-color"],
        capture_output=True, text=True
    )
    log_file = LOG_DIR / f"{app_name}.log"
    log_file.write_text(result.stdout + result.stderr, encoding="utf-8")
    print(f"  容器日志已保存至: {log_file}")


def get_port(app_dir: Path) -> str | None:
    env_file = app_dir / ".env"
    if not env_file.exists():
        return None
    load_dotenv(dotenv_path=str(env_file), override=True)
    return os.getenv("W9_HTTP_PORT_SET")


def wait_for_http(app_name: str, port: str) -> tuple[bool, int]:
    """轮询直到成功或超时，返回 (success, final_status_code)"""
    url = f"http://localhost:{port}"
    elapsed = 0
    while elapsed < MAX_WAIT_SECONDS:
        try:
            resp = requests.get(url, timeout=5, allow_redirects=False)
            print(f"  [{elapsed:3d}s] {url} → {resp.status_code}")
            if resp.status_code in SUCCESS_CODES:
                return True, resp.status_code
        except requests.exceptions.ConnectionError:
            print(f"  [{elapsed:3d}s] 连接拒绝，等待启动...")
        except requests.exceptions.Timeout:
            print(f"  [{elapsed:3d}s] 请求超时，继续等待...")
        except Exception as e:
            print(f"  [{elapsed:3d}s] 请求异常: {e}")
        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL
    return False, 0


# ─── 核心逻辑 ────────────────────────────────────────────────

def test_app(app_name: str) -> bool:
    print(f"\n{'#'*60}")
    print(f"  测试: {app_name}")
    print(f"{'#'*60}")

    app_dir = Path("apps") / app_name
    if not app_dir.is_dir():
        print(f"  [FAIL] 目录不存在: {app_dir}")
        return False

    # 获取端口
    port = get_port(app_dir)
    if not port:
        print("  [SKIP] .env 中无 W9_HTTP_PORT_SET，跳过 HTTP 测试")
        return True

    # 启动
    print(f"  启动 docker compose up -d ...")
    if not compose_up(app_dir):
        save_logs(app_name, app_dir)
        compose_down(app_dir)
        return False

    # 等待 HTTP
    print(f"  等待 http://localhost:{port}（最长 {MAX_WAIT_SECONDS}s）...")
    success, code = wait_for_http(app_name, port)

    if success:
        print(f"  [PASS] HTTP {code} ✓")
    else:
        print(f"  [FAIL] 超时 {MAX_WAIT_SECONDS}s 未收到成功响应")
        save_logs(app_name, app_dir)

    # 清理（无论成功失败）
    print("  清理 docker compose down -v ...")
    compose_down(app_dir)

    return success


def main():
    # 获取 app 列表（命令行参数优先，其次环境变量）
    if len(sys.argv) > 1:
        raw = sys.argv[1]
    else:
        raw = os.getenv("APP_LISTS", "")

    if not raw.strip():
        print("ERROR: 未指定应用列表", file=sys.stderr)
        print("用法: python3 build/test_apps.py \"wordpress,nginx\"", file=sys.stderr)
        sys.exit(2)

    app_names = [a.strip() for a in raw.split(",") if a.strip()]

    results = {}
    for app in app_names:
        results[app] = test_app(app)

    # 汇总
    print(f"\n{'='*60}")
    print("  测试결果汇总")
    print(f"{'='*60}")
    for app, passed in results.items():
        icon = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {icon}  {app}")
    print(f"{'='*60}")

    failed_count = sum(1 for v in results.values() if not v)
    print(f"\n  {len(results)} 个应用，{failed_count} 个失败\n")

    sys.exit(1 if failed_count > 0 else 0)


if __name__ == "__main__":
    main()
