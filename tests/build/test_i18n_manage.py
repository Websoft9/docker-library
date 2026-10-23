from __future__ import annotations

import importlib.util
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "i18n" / "manage.py"


def load_manage():
    spec = importlib.util.spec_from_file_location("i18n_manage", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_parse_env_keys_only_returns_translatable_keys():
    manage = load_manage()

    keys = manage.parse_env_keys(
        "W9_HTTP_PORT_SET=9001\n"
        "W9_LOGIN_USER=admin\n"
        "APP_SECRET=value\n"
        "# W9_COMMENTED_SET=9003\n"
    )

    assert keys == {"W9_HTTP_PORT_SET", "W9_LOGIN_USER"}


def test_added_env_keys_ignores_context_and_removed_lines():
    manage = load_manage()
    diff = """diff --git a/apps/demo/.env b/apps/demo/.env
@@ -1 +1,3 @@
-W9_OLD_SET=1
+W9_NEW_SET=2
+APP_SECRET=value
"""

    assert manage.added_env_keys(diff) == {"W9_NEW_SET"}


def test_untranslated_keys_reports_empty_values():
    manage = load_manage()

    assert manage.untranslated_keys(
        {"W9_HTTP_PORT_SET", "W9_LOGIN_USER"},
        {"W9_HTTP_PORT_SET": ["HTTP Port", "HTTP 端口"], "W9_LOGIN_USER": ["", "用户"]},
    ) == ["W9_LOGIN_USER"]


def test_check_and_update_use_translation_file(tmp_path, monkeypatch):
    manage = load_manage()
    monkeypatch.setattr(manage, "ROOT", tmp_path)
    app = tmp_path / "apps" / "demo"
    app.mkdir(parents=True)
    (app / ".env").write_text("W9_HTTP_PORT_SET=9001\nW9_SSH_PORT_SET=9022\n", encoding="utf-8")
    translation = tmp_path / "translation.json"
    translation.write_text(json.dumps({"W9_HTTP_PORT_SET": ["", ""]}), encoding="utf-8")

    assert manage.main(["--check", "--translation", str(translation)]) == 1
    assert manage.main(["--check", "--app", "demo", "--json", "--translation", str(translation)]) == 1

    assert manage.main(["--update", "--translation", str(translation)]) == 0
    updated = json.loads(translation.read_text(encoding="utf-8"))
    assert updated["W9_SSH_PORT_SET"] == ["", ""]
    assert manage.main(["--check", "--translation", str(translation)]) == 0
    assert manage.main(["--check", "--strict", "--translation", str(translation)]) == 1


def test_check_emits_github_annotations(tmp_path, monkeypatch, capsys):
    manage = load_manage()
    monkeypatch.setattr(manage, "ROOT", tmp_path)
    app = tmp_path / "apps" / "demo"
    app.mkdir(parents=True)
    (app / ".env").write_text("W9_HTTP_PORT_SET=9001\nW9_SSH_PORT_SET=9022\n", encoding="utf-8")
    translation = tmp_path / "translation.json"
    translation.write_text(json.dumps({"W9_HTTP_PORT_SET": ["", ""]}), encoding="utf-8")

    assert manage.main(["--check", "--github-annotations", "--translation", str(translation)]) == 1

    output = capsys.readouterr().out
    assert "::error file=apps/demo/.env,title=Missing i18n keys::W9_SSH_PORT_SET" in output
    assert "::warning file=apps/demo/.env,title=Untranslated i18n keys::W9_HTTP_PORT_SET" in output


def test_warn_only_emits_warnings_and_exits_zero(tmp_path, monkeypatch, capsys):
    manage = load_manage()
    monkeypatch.setattr(manage, "ROOT", tmp_path)
    app = tmp_path / "apps" / "demo"
    app.mkdir(parents=True)
    (app / ".env").write_text("W9_HTTP_PORT_SET=9001\nW9_SSH_PORT_SET=9022\n", encoding="utf-8")
    translation = tmp_path / "translation.json"
    translation.write_text(json.dumps({"W9_HTTP_PORT_SET": ["", ""]}), encoding="utf-8")

    assert manage.main([
        "--check", "--github-annotations", "--warn-only", "--translation", str(translation)
    ]) == 0

    output = capsys.readouterr().out
    assert "::warning file=apps/demo/.env,title=Missing i18n keys::W9_SSH_PORT_SET" in output
    assert "::warning file=apps/demo/.env,title=Untranslated i18n keys::W9_HTTP_PORT_SET" in output
