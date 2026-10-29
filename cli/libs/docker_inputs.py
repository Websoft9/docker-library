"""Resolve the files that actually feed a Dockerfile build.

A build is identified by its inputs, not by the whole app directory or a commit
SHA: the Dockerfile, the context files it copies in, the injected version build
argument, and the base image references. A README or catalog edit therefore
reuses the existing image instead of rebuilding it.

This module is standard-library only so CI scripts can import it without
installing the CLI.
"""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import posixpath
import re
import shlex
import subprocess
import sys
from pathlib import Path

APP_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
TAG_PREFIX = "dev-src-"
HASH_LENGTH = 16
CONTINUATION_RE = re.compile(r"\\\s*$")
INSTRUCTION_RE = re.compile(r"^(COPY|ADD|FROM)\s+(.*)$", re.IGNORECASE)
URL_PREFIXES = ("http://", "https://", "git@", "ssh://", "ftp://")


def _git(*args: str, binary: bool = False) -> bytes | str:
    result = subprocess.run(["git", *args], capture_output=True, check=False)
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(detail or f"git {' '.join(args)} failed")
    return result.stdout if binary else result.stdout.decode("utf-8")


def repo_root() -> Path:
    try:
        return Path(str(_git("rev-parse", "--show-toplevel")).strip())
    except RuntimeError:
        current = Path.cwd().resolve()
        for candidate in (current, *current.parents):
            if (candidate / "apps").is_dir() and (candidate / "metadata").is_dir():
                return candidate
        return current


def _validate_app(app: str) -> str:
    if not APP_RE.fullmatch(app):
        raise ValueError(f"Invalid app name: {app}")
    return app


def _blob_digest(data: bytes) -> str:
    """Git-compatible blob identity so worktree and ref hashes agree."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _app_files(app: str, ref: str | None) -> dict[str, str]:
    """Map app-relative path -> content digest for the given git ref."""
    if ref:
        listing = str(_git("ls-tree", "-r", ref, "--", f"apps/{app}"))
        prefix = f"apps/{app}/"
        files: dict[str, str] = {}
        for line in listing.splitlines():
            if not line.strip():
                continue
            meta, path = line.split("\t", 1)
            _, kind, digest = meta.split()
            if kind != "blob" or not path.startswith(prefix):
                continue
            files[path[len(prefix):]] = digest
        return files

    root = repo_root() / "apps" / app
    if not root.is_dir():
        raise ValueError(f"app not found: apps/{app}")
    files = {}
    for path in sorted(root.rglob("*")):
        if ".git" in path.parts or path.is_dir():
            continue
        files[path.relative_to(root).as_posix()] = _blob_digest(path.read_bytes())
    return files


def _read(app: str, relative: str, ref: str | None) -> bytes:
    if ref:
        try:
            return _git("show", f"{ref}:apps/{app}/{relative}", binary=True)  # type: ignore[return-value]
        except RuntimeError as error:
            raise ValueError(f"cannot read apps/{app}/{relative} at {ref}") from error
    return (repo_root() / "apps" / app / relative).read_bytes()


def _logical_lines(text: str):
    buffer = ""
    for raw in text.splitlines():
        line = raw.rstrip()
        if not buffer and (not line.strip() or line.lstrip().startswith("#")):
            continue
        if CONTINUATION_RE.search(line):
            buffer += line[:-1].rstrip() + " "
            continue
        buffer += line
        yield buffer.strip()
        buffer = ""
    if buffer.strip():
        yield buffer.strip()


def _instructions(text: str):
    """Yield (kind, sources, base_image, from_other_stage, unsafe)."""
    for line in _logical_lines(text):
        match = INSTRUCTION_RE.match(line)
        if not match:
            continue
        kind = match.group(1).upper()
        rest = match.group(2).strip()
        if kind == "FROM":
            tokens = [token for token in rest.split() if not token.startswith("--")]
            if tokens:
                yield kind, [], tokens[0], False, False
            continue
        if rest.startswith("["):
            try:
                tokens = json.loads(rest)
            except json.JSONDecodeError:
                yield kind, [], "", False, True
                continue
        else:
            try:
                tokens = shlex.split(rest)
            except ValueError:
                yield kind, [], "", False, True
                continue
        flags = [token for token in tokens if token.startswith("--")]
        parts = [token for token in tokens if not token.startswith("--")]
        from_other_stage = any(flag.startswith("--from") for flag in flags)
        unsafe = any(flag.startswith("--exclude") for flag in flags) or len(parts) < 2
        yield kind, parts[:-1], "", from_other_stage, unsafe


def _ignore_patterns(text: str | None) -> list[str] | None:
    if text is None:
        return []
    patterns = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("!"):
            # Negation needs real dockerignore evaluation; fall back to the
            # whole context so the identity stays correct.
            return None
        patterns.append(line.lstrip("./").rstrip("/"))
    return patterns


def _ignored(path: str, patterns: list[str]) -> bool:
    for pattern in patterns:
        if not pattern:
            continue
        if fnmatch.fnmatchcase(path, pattern):
            return True
        if path.startswith(pattern + "/"):
            return True
        if "/" not in pattern and fnmatch.fnmatchcase(posixpath.basename(path), pattern):
            return True
    return False


def _resolve_source(source: str, files: dict[str, str]) -> tuple[set[str], bool]:
    """Return (matched files, unsafe). Unsafe means: use the whole context."""
    value = source.strip()
    if not value:
        return set(), False
    if value.lower().startswith(URL_PREFIXES):
        return set(), False
    if "$" in value:
        return set(), True
    while value.startswith("./"):
        value = value[2:]
    normalized = posixpath.normpath(value)
    if normalized in ("", "."):
        return set(files), False
    if normalized.startswith("../"):
        return set(), True
    if any(char in normalized for char in "*?["):
        matched = {path for path in files if fnmatch.fnmatchcase(path, normalized)}
        return (matched, False) if matched else (set(), True)
    if normalized in files:
        return {normalized}, False
    prefix = normalized + "/"
    nested = {path for path in files if path.startswith(prefix)}
    return (nested, False) if nested else (set(), True)


def _env_values(text: str) -> dict[str, str]:
    values = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip("'").strip('"')
    return values


def resolve_inputs(app: str, ref: str | None = None) -> dict:
    """Return the build-input identity for one app at a git ref."""
    _validate_app(app)
    files = _app_files(app, ref)
    if "Dockerfile" not in files:
        raise ValueError(f"apps/{app} has no root Dockerfile")

    dockerfile = _read(app, "Dockerfile", ref).decode("utf-8", "replace")
    inputs: set[str] = {"Dockerfile", ".dockerignore"} if ".dockerignore" in files else {"Dockerfile"}
    ignore = _ignore_patterns(
        _read(app, ".dockerignore", ref).decode("utf-8", "replace") if ".dockerignore" in files else None
    )

    from_images: list[str] = []
    conservative = False
    for kind, sources, base_image, from_other_stage, unsafe in _instructions(dockerfile):
        if kind == "FROM":
            if base_image:
                from_images.append(base_image)
            continue
        if from_other_stage:
            continue
        if unsafe:
            conservative = True
            break
        for source in sources:
            matched, risky = _resolve_source(source, files)
            if risky:
                conservative = True
                break
            inputs.update(matched)
        if conservative:
            break

    if conservative:
        inputs = set(files)
        inputs.add("Dockerfile")
    elif ignore:
        kept = {path for path in inputs if path == "Dockerfile" or not _ignored(path, ignore)}
        inputs = kept or set(files)

    env = _env_values(_read(app, ".env", ref).decode("utf-8", "replace")) if ".env" in files else {}
    version = env.get("W9_VERSION", "")
    version_arg = f"{app.upper()}_VERSION"

    lines = [f"file\t{path}\t{files[path]}" for path in sorted(inputs)]
    lines.append(f"arg\t{version_arg}={version}")
    if env.get("W9_REPO"):
        lines.append(f"repo\t{env['W9_REPO']}")
    for image in sorted(set(from_images)):
        lines.append(f"from\t{image}")
    digest = hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()

    return {
        "app": app,
        "ref": ref or "WORKTREE",
        "hash": digest,
        "tag": f"{TAG_PREFIX}{digest[:HASH_LENGTH]}",
        "files": sorted(inputs),
        "version": version,
        "version_arg": version_arg,
        "from": sorted(set(from_images)),
        "conservative": conservative,
    }


def context_tag(app: str, ref: str | None = None) -> str:
    return str(resolve_inputs(app, ref)["tag"])


def changed_apps(base: str, head: str) -> list[str]:
    """Apps whose build inputs differ between two refs."""
    diff = str(_git("diff", "--name-only", base, head, "--", "apps"))
    names = set()
    for path in diff.splitlines():
        parts = path.split("/")
        if len(parts) > 2 and parts[0] == "apps":
            names.add(parts[1])

    changed = []
    for app in sorted(names):
        if not APP_RE.fullmatch(app):
            continue
        after_files = _app_files(app, head)
        if "Dockerfile" not in after_files:
            # Only a confirmed absence means there is nothing to build.
            continue
        after = resolve_inputs(app, head)
        if "Dockerfile" not in _app_files(app, base):
            changed.append(app)
            continue
        before = resolve_inputs(app, base)
        if before["hash"] != after["hash"]:
            changed.append(app)
    return changed


def all_buildable_apps(ref: str | None = None) -> list[str]:
    root = repo_root() / "apps"
    return sorted(
        path.name for path in root.iterdir() if path.is_dir() and (path / "Dockerfile").is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Resolve Dockerfile build inputs")
    parser.add_argument("--app")
    parser.add_argument("--ref", default=None)
    parser.add_argument("--changed", action="store_true")
    parser.add_argument("--base")
    parser.add_argument("--head", default="HEAD")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.changed:
            if not args.base:
                parser.error("--changed requires --base")
            apps = changed_apps(args.base, args.head)
            payload: dict = {"apps": apps, "matrix": apps}
        elif args.all:
            apps = all_buildable_apps(args.ref)
            payload = {
                "apps": apps,
                "matrix": apps,
                "inputs": {app: resolve_inputs(app, args.ref) for app in apps},
            }
        elif args.app:
            payload = resolve_inputs(args.app, args.ref)
        else:
            parser.error("one of --app, --changed, or --all is required")
            return 2
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print("\n".join(payload.get("apps", [])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
