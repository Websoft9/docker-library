#!/usr/bin/env python3
"""Send best-effort WeCom markdown notifications using the shared WECOM_WEBHOOK."""
from __future__ import annotations

import argparse
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

MARKDOWN_LIMIT = 4096  # WeCom counts UTF-8 bytes, not characters.


def truncate(text: str, limit: int = MARKDOWN_LIMIT, suffix: str = "\n…") -> str:
    if len(text.encode("utf-8")) <= limit:
        return text
    budget = max(0, limit - len(suffix.encode("utf-8")))
    return text.encode("utf-8")[:budget].decode("utf-8", errors="ignore") + suffix


def release_message(repository: str, tag: str, release_url: str, run_url: str, notes: str) -> str:
    header = (
        f"# Appstore 发布成功：{tag}\n"
        f"> 仓库：{repository}\n"
        f"> [Release 与完整说明]({release_url})\n"
        "> [Appstore 制品](https://artifact.websoft9.com/release/websoft9/plugin/library/library-latest.zip)\n"
        f"> [发布运行记录]({run_url})\n\n"
        "## Release notes\n"
    )
    notes = re.sub(r"<!--.*?-->", "", notes, flags=re.DOTALL).strip()
    notes = notes or "本次发布未填写说明，请查看 Release 页面。"
    suffix = "\n…（内容已截断，完整说明见 Release）"
    budget = max(0, MARKDOWN_LIMIT - len(header.encode("utf-8")))
    return truncate(header + truncate(notes, budget, suffix))


def send_markdown(content: str, webhook: str) -> bool:
    if not webhook:
        print("::warning::WECOM_WEBHOOK is not set; skipping notification")
        return False
    payload = json.dumps({"msgtype": "markdown", "markdown": {"content": truncate(content)}},
                         ensure_ascii=False).encode("utf-8")
    # Do not log exceptions or server messages: they may contain the secret URL.
    for attempt in range(3):
        try:
            request = urllib.request.Request(webhook, data=payload, headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(request, timeout=2) as response:
                result = json.load(response)
            if isinstance(result, dict) and result.get("errcode") == 0:
                print("WeCom notification sent")
                return True
        except (urllib.error.URLError, OSError, ValueError):
            pass
        if attempt < 2:
            time.sleep(1)
    print("::warning::WeCom notification failed after 3 attempts; publishing result is unchanged")
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--markdown-file", type=Path)
    source.add_argument("--release-notes-file", type=Path)
    args = parser.parse_args()
    try:
        if args.release_notes_file:
            content = release_message(
                os.environ["REPOSITORY"], os.environ["RELEASE_TAG"], os.environ["RELEASE_URL"],
                os.environ["RUN_URL"], args.release_notes_file.read_text(encoding="utf-8"),
            )
        else:
            content = args.markdown_file.read_text(encoding="utf-8")
        send_markdown(content, os.environ.get("WECOM_WEBHOOK", ""))
    except (OSError, ValueError, KeyError):
        print("::warning::Could not prepare WeCom notification")


if __name__ == "__main__":
    main()
