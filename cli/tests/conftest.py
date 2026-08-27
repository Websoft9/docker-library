from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from libs import repo


@pytest.fixture(autouse=True)
def clear_repo_root_cache():
    repo.repo_root.cache_clear()
    yield
    repo.repo_root.cache_clear()


@pytest.fixture
def repo_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    for marker in ("apps", "metadata", "i18n", "archive/apps"):
        (tmp_path / marker).mkdir(parents=True, exist_ok=True)
    (tmp_path / "library.json").write_text("{}\n", encoding="utf-8")
    (tmp_path / "metadata" / "maintenance.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"status": "active", "cadence": "monthly", "update_policy": "patch-minor"},
                "cadence": {},
                "update_policy": {},
                "lifecycle": {"frozen": []},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "metadata" / "archive.yaml").write_text(
        yaml.safe_dump(
            {
                "defaults": {"archive_reason": "owner-retired", "contentful": {"action": "archive", "production": False}},
                "apps": [],
                "overrides": {},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "i18n" / "translation.json").write_text("{}\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


@pytest.fixture
def app_factory(repo_fixture: Path):
    def create_app(
        name: str,
        *,
        env: str = "W9_URL=''\n",
        compose: str = "services: {}\n",
        variables: dict | None = None,
        readme: str = "# README\n",
        archived: bool = False,
    ) -> Path:
        root = repo_fixture / ("archive/apps" if archived else "apps") / name
        root.mkdir(parents=True, exist_ok=True)
        (root / ".env").write_text(env, encoding="utf-8")
        (root / "docker-compose.yml").write_text(compose, encoding="utf-8")
        if variables is None:
            variables = {
                "name": name,
                "trademark": name.title(),
                "release": True,
                "upstream": {"image": "https://hub.docker.com/_/example/tags"},
                "edition": [{"dist": "community", "version": ["1.0"]}],
            }
        (root / "variables.json").write_text(json.dumps(variables, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (root / "README.md").write_text(readme, encoding="utf-8")
        (root / "CHANGELOG.md").write_text("# CHANGELOG\n", encoding="utf-8")
        return root

    return create_app
