from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def build_fixture(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    (tmp_path / "apps" / "demo").mkdir(parents=True)
    (tmp_path / "apps" / "demo" / "variables.json").write_text(
        json.dumps(
            {
                "name": "demo",
                "trademark": "Demo App",
                "release": True,
                "edition": [{"dist": "community", "version": ["1.0", "latest"]}],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "archive" / "apps" / "archived-demo").mkdir(parents=True)
    (tmp_path / "metadata").mkdir(parents=True, exist_ok=True)
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
                "apps": ["archived-demo"],
                "overrides": {},
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (tmp_path / "library.json").write_text('{"Version": "1.0.0"}\n', encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path
