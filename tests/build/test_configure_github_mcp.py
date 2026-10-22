from __future__ import annotations

import stat

import pytest

from _helpers import REPO_ROOT, load_build_module

configure = load_build_module("configure_github_mcp", REPO_ROOT / "ci" / "scripts" / "configure_github_mcp.py")


def test_write_token_sets_exact_token_and_mode(tmp_path):
    path = tmp_path / "github.token"

    configure.write_token(path, "  ghp_test  ")

    assert path.read_text(encoding="utf-8") == "ghp_test"
    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_update_config_header_replaces_existing_authorization(tmp_path):
    token_file = tmp_path / "github.token"
    text = (
        '{"mcp":{"github":{"type":"remote",'
        '"headers":{"Authorization":"Bearer {env:GITHUB_PERSONAL_ACCESS_TOKEN}"}}}}'
    )

    updated = configure.update_config_header(text, token_file)

    assert f"Bearer {{file:{token_file}}}" in updated
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" not in updated


def test_update_config_header_requires_github_block(tmp_path):
    with pytest.raises(ValueError, match="GitHub MCP block"):
        configure.update_config_header('{"mcp":{}}', tmp_path / "github.token")


def test_ensure_config_creates_missing_file(tmp_path):
    config = tmp_path / "opencode.jsonc"
    token_file = tmp_path / "github.token"

    assert configure.ensure_config(config, token_file) is True

    text = config.read_text(encoding="utf-8")
    assert '"github"' in text
    assert f"Bearer {{file:{token_file}}}" in text


def test_ensure_config_backs_up_before_update(tmp_path):
    config = tmp_path / "opencode.jsonc"
    token_file = tmp_path / "github.token"
    config.write_text(
        '{\n'
        '  "mcp": {\n'
        '    "github": {\n'
        '      "type": "remote",\n'
        '      "headers": {\n'
        '        "Authorization": "Bearer {env:GITHUB_PERSONAL_ACCESS_TOKEN}"\n'
        "      }\n"
        "    }\n"
        "  }\n"
        "}\n",
        encoding="utf-8",
    )

    assert configure.ensure_config(config, token_file) is True

    assert config.with_suffix(".jsonc.bak").exists()
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" not in config.read_text(encoding="utf-8")
