#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TRANSLATION = ROOT / "i18n" / "translation.json"
TRANSLATABLE_KEY_RE = re.compile(r"^(W9_.*_SET|W9_LOGIN.*)$")
ENV_LINE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")


def is_translatable(key: str) -> bool:
    return bool(TRANSLATABLE_KEY_RE.match(key))


def parse_env_keys(text: str) -> set[str]:
    keys: set[str] = set()
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = ENV_LINE_RE.match(line)
        if match and is_translatable(match.group(1)):
            keys.add(match.group(1))
    return keys


def added_env_keys(diff_text: str) -> set[str]:
    keys: set[str] = set()
    for line in diff_text.splitlines():
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:].strip()
        if not content or content.startswith("#"):
            continue
        match = ENV_LINE_RE.match(content)
        if match and is_translatable(match.group(1)):
            keys.add(match.group(1))
    return keys


def missing_keys(keys: set[str], translation: dict) -> list[str]:
    return sorted(key for key in keys if key not in translation)


def untranslated_keys(keys: set[str], translation: dict) -> list[str]:
    """Return keys whose English or Chinese translation is still empty."""
    result = []
    for key in sorted(keys):
        values = translation.get(key)
        if not isinstance(values, list) or len(values) < 2:
            continue
        if not str(values[0]).strip() or not str(values[1]).strip():
            result.append(key)
    return result


def app_from_path(path: Path) -> str:
    parts = path.parts
    if "apps" in parts:
        index = parts.index("apps")
        if index + 1 < len(parts):
            return parts[index + 1]
    return ""


def app_env_files(app: str | None = None) -> list[Path]:
    files = sorted((ROOT / "apps").glob("*/.env"))
    if app:
        return [path for path in files if app_from_path(path) == app]
    return files


def changed_env_files(base: str, head: str, app: str | None = None) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base, head, "--", "apps/*/.env"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    files = [ROOT / line for line in result.stdout.splitlines() if line.strip()]
    if app:
        files = [path for path in files if app_from_path(path) == app]
    return files


def file_added_keys(base: str, head: str, path: Path) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--unified=0", base, head, "--", str(path.relative_to(ROOT))],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return added_env_keys(result.stdout)


def collect_keys(
    *,
    base: str | None = None,
    head: str | None = None,
    app: str | None = None,
) -> dict[str, set[str]]:
    if bool(base) != bool(head):
        raise ValueError("--base and --head must be provided together")
    if base and head:
        files = changed_env_files(base, head, app)
        return {app_from_path(path): file_added_keys(base, head, path) for path in files}
    return {app_from_path(path): parse_env_keys(path.read_text(encoding="utf-8")) for path in app_env_files(app)}


def write_translation(path: Path, translation: dict) -> None:
    path.write_text(json.dumps(translation, indent=4, ensure_ascii=False), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check or update i18n/translation.json for W9_*_SET and W9_LOGIN* env keys."
    )
    parser.add_argument("--check", action="store_true", help="Check only; exit 1 when keys are missing")
    parser.add_argument("--update", action="store_true", help='Add missing keys as ["", ""]')
    parser.add_argument("--base", help="Base commit SHA; only inspect keys added between base and head")
    parser.add_argument("--head", help="Head commit SHA; only inspect keys added between base and head")
    parser.add_argument("--app", help="Limit to one app")
    parser.add_argument("--translation", type=Path, default=DEFAULT_TRANSLATION, help="translation.json path")
    parser.add_argument("--strict", action="store_true", help="Fail when a used key has an empty translation")
    parser.add_argument("--github-annotations", action="store_true", help="Emit GitHub error/warning annotations")
    parser.add_argument("--warn-only", action="store_true", help="Never fail on missing or untranslated keys")
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args(argv)

    if not args.check and not args.update:
        parser.error("pass --check or --update")

    translation_path = args.translation if args.translation.is_absolute() else ROOT / args.translation
    if not translation_path.exists():
        print(f"missing translation file: {translation_path}", file=sys.stderr)
        return 1
    translation = json.loads(translation_path.read_text(encoding="utf-8"))

    try:
        keys_by_app = collect_keys(base=args.base, head=args.head, app=args.app)
    except (ValueError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        return 2

    missing_by_app = {}
    untranslated_by_app = {}
    for app, keys in sorted(keys_by_app.items()):
        missing = missing_keys(keys, translation)
        if missing:
            missing_by_app[app] = missing
        untranslated = untranslated_keys(keys, translation)
        if untranslated:
            untranslated_by_app[app] = untranslated

    if args.update:
        added = []
        for app, keys in sorted(missing_by_app.items()):
            for key in keys:
                translation[key] = ["", ""]
                added.append({"app": app, "key": key})
        if added:
            write_translation(translation_path, translation)
        if args.json:
            print(json.dumps({
                "updated": added,
                "untranslated": untranslated_by_app,
                "translation": str(translation_path.relative_to(ROOT)),
            }, indent=2, ensure_ascii=False))
        else:
            for item in added:
                print(f"added {item['key']} ({item['app']})")
            if not added:
                print("no missing i18n keys")
            for app, keys in sorted(untranslated_by_app.items()):
                print(f"needs translation ({app}): {', '.join(keys)}")
        return 0

    ok = not missing_by_app
    strict_ok = ok and not untranslated_by_app
    if args.json:
        print(json.dumps({
            "missing": missing_by_app,
            "untranslated": untranslated_by_app,
            "ok": ok,
            "strict_ok": strict_ok,
        }, indent=2, ensure_ascii=False))
    elif args.github_annotations:
        missing_level = "warning" if args.warn_only else "error"
        for app, keys in sorted(missing_by_app.items()):
            joined = ", ".join(keys)
            print(f"::{missing_level} file=apps/{app}/.env,title=Missing i18n keys::{joined}")
        for app, keys in sorted(untranslated_by_app.items()):
            joined = ", ".join(keys)
            print(f"::warning file=apps/{app}/.env,title=Untranslated i18n keys::{joined}")
        if missing_by_app:
            print("add missing keys to i18n/translation.json (empty values are allowed)", file=sys.stderr)
        elif untranslated_by_app and not args.strict:
            print("some keys still have empty translations; use --strict to fail on them", file=sys.stderr)
    else:
        for app, keys in sorted(missing_by_app.items()):
            print(f"missing ({app}): {', '.join(keys)}")
        for app, keys in sorted(untranslated_by_app.items()):
            print(f"needs translation ({app}): {', '.join(keys)}")
        if missing_by_app:
            print("add missing keys to i18n/translation.json (empty values are allowed)", file=sys.stderr)
        elif untranslated_by_app and not args.strict:
            print("some keys still have empty translations; use --strict to fail on them", file=sys.stderr)
        if ok and not untranslated_by_app:
            print("i18n keys OK")
        elif ok:
            print("i18n keys registered; translations pending")
    if args.warn_only:
        return 0
    return 0 if (strict_ok if args.strict else ok) else 1


if __name__ == "__main__":
    raise SystemExit(main())
