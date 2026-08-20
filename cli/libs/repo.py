from __future__ import annotations

from functools import lru_cache
from pathlib import Path


REPO_MARKERS = ("apps", "metadata", "i18n", "library.json")


@lru_cache(maxsize=1)
def repo_root() -> Path:
    current = Path.cwd().resolve()
    for candidate in (current, *current.parents):
        if all((candidate / marker).exists() for marker in REPO_MARKERS):
            return candidate
    raise FileNotFoundError(
        "docker-library repository root not found; run libs from the repository root or one of its subdirectories"
    )


def repo_path(*parts: str) -> Path:
    return repo_root().joinpath(*parts)


def relative_repo_path(path: Path) -> str:
    try:
        return str(path.relative_to(repo_root()))
    except ValueError:
        return str(path)
