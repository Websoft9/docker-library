from __future__ import annotations

import json

from libs import validate


def test_structure_result_detects_missing_files_and_missing_src_mount(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  web:\n"
            "    volumes:\n"
            "      - ./src/init.sh:/data/init.sh\n"
        ),
    )
    (app_path / "README.md").unlink()

    result = validate._structure_result(app_path)

    assert result["ok"] is False
    assert result["missing_files"] == ["README.md"]
    assert result["missing_src"] == ["src/init.sh"]


def test_policy_result_checks_translations_login_pair_and_url_replace(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env=(
            "W9_NAME_SET=Name\n"
            "W9_LOGIN_USER=admin\n"
            "W9_URL_REPLACE=true\n"
        ),
        compose="services: {}\n",
    )
    (repo_fixture / "i18n" / "translation.json").write_text(json.dumps({"OTHER_KEY": ["", ""]}) + "\n", encoding="utf-8")

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["missing_translation_keys"] == ["W9_NAME_SET", "W9_LOGIN_USER"]
    assert result["login_pair_ok"] is False
    assert result["url_replace_ok"] is False


def test_check_app_returns_gate_specific_payload(repo_fixture, app_factory):
    app_factory("demo")

    structure = validate.check_app("demo", gate="structure")
    policy = validate.check_app("demo", gate="policy")
    all_result = validate.check_app("demo", gate="all")

    assert structure["gate"] == "structure"
    assert policy["gate"] == "policy"
    assert all_result["ok"] is True
