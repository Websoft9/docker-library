#!/usr/bin/env python3
"""Configure the GitHub MCP token used by opencode."""

from __future__ import annotations

import argparse
import getpass
import os
import re
import shutil
import sys
import urllib.error
import urllib.request
from pathlib import Path

MCP_URL = "https://api.githubcopilot.com/mcp/"


def config_dir() -> Path:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "opencode"


def config_path() -> Path:
    directory = config_dir()
    for name in ("opencode.jsonc", "opencode.json"):
        candidate = directory / name
        if candidate.exists():
            return candidate
    return directory / "opencode.jsonc"


def token_path() -> Path:
    return config_dir() / "github.token"


def write_token(path: Path, token: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(token.strip())
    os.chmod(path, 0o600)


def _github_block(text: str) -> tuple[int, int] | None:
    match = re.search(r'"github"\s*:\s*\{', text)
    if not match:
        return None

    start = text.index("{", match.start())
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return start, index
    return None


def update_config_header(text: str, token_file: Path) -> str:
    block = _github_block(text)
    if not block:
        raise ValueError("GitHub MCP block not found in opencode config")

    start, end = block
    body = text[start : end + 1]
    header = f"Bearer {{file:{token_file}}}"
    pattern = re.compile(r'("Authorization"\s*:\s*")[^"]*(")')
    if not pattern.search(body):
        raise ValueError("GitHub MCP Authorization header not found in opencode config")

    body = pattern.sub(lambda match: match.group(1) + header + match.group(2), body, count=1)
    return text[:start] + body + text[end + 1 :]


def ensure_config(path: Path, token_file: Path) -> bool:
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "{\n"
            '  "$schema": "https://opencode.ai/config.json",\n'
            '  "mcp": {\n'
            '    "github": {\n'
            '      "type": "remote",\n'
            f'      "url": "{MCP_URL}",\n'
            '      "enabled": true,\n'
            '      "oauth": false,\n'
            '      "headers": {\n'
            f'        "Authorization": "Bearer {{file:{token_file}}}"\n'
            "      }\n"
            "    }\n"
            "  }\n"
            "}\n",
            encoding="utf-8",
        )
        return True

    original = path.read_text(encoding="utf-8")
    updated = update_config_header(original, token_file)
    if updated == original:
        return False

    backup = path.with_suffix(path.suffix + ".bak")
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")
    return True


def verify_token(token: str) -> tuple[bool | None, str]:
    request = urllib.request.Request(
        MCP_URL,
        headers={"Authorization": f"Bearer {token}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return True, f"reachable (HTTP {response.status})"
    except urllib.error.HTTPError as error:
        if error.code == 401:
            return False, "invalid token (HTTP 401)"
        return True, f"reachable (HTTP {error.code})"
    except Exception as error:
        return None, f"not verified ({error})"


def read_token() -> str:
    token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "").strip()
    if token:
        return token
    return getpass.getpass("GitHub personal access token: ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-verify", action="store_true", help="skip the GitHub MCP reachability check")
    args = parser.parse_args()

    token = read_token()
    if not token:
        print("empty token is not allowed", file=sys.stderr)
        return 1

    token_file = token_path()
    write_token(token_file, token)
    print(f"wrote {token_file}")

    cfg = config_path()
    try:
        changed = ensure_config(cfg, token_file)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        print(
            "Add a GitHub MCP block with an Authorization header to "
            f"{cfg}, then rerun this target.",
            file=sys.stderr,
        )
        return 1

    if changed:
        print(f"updated {cfg}")
        print(f"backup: {cfg.with_suffix(cfg.suffix + '.bak')}")
    else:
        print(f"already configured: {cfg}")

    if not args.no_verify:
        valid, message = verify_token(token)
        print(f"token check: {message}")
        if valid is False:
            return 1

    print("restart opencode, then run: opencode mcp list")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
