from __future__ import annotations

import pytest

from libs import credentials


def test_load_provider_env_parses_default_file(repo_fixture):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "contentful.env").write_text(
        "# comment line\nCONTENTFUL_ACCESS_TOKEN=\"abc\"\nEMPTY=\n",
        encoding="utf-8",
    )

    data = credentials.load_provider_env("contentful")

    assert data["CONTENTFUL_ACCESS_TOKEN"] == "abc"
    assert data["EMPTY"] == ""


def test_load_provider_env_supports_explicit_env_file(repo_fixture):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "custom-cloudflare.env").write_text(
        "CLOUDFLARE_API_TOKEN='xyz'\n",
        encoding="utf-8",
    )

    data = credentials.load_provider_env("cloudflare", ".secrets/custom-cloudflare.env")

    assert data["CLOUDFLARE_API_TOKEN"] == "xyz"


def test_load_provider_env_missing_file_is_empty(repo_fixture):
    assert credentials.load_provider_env("contentful") == {}


def test_resolve_secret_precedence(repo_fixture, monkeypatch):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "contentful.env").write_text(
        "CONTENTFUL_ACCESS_TOKEN=default-token\n",
        encoding="utf-8",
    )
    (repo_fixture / ".secrets" / "custom-contentful.env").write_text(
        "CONTENTFUL_ACCESS_TOKEN=file-token\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("CONTENTFUL_ACCESS_TOKEN", "env-token")

    assert credentials.resolve_secret("CONTENTFUL_ACCESS_TOKEN", "contentful", "flag-token") == "flag-token"
    assert credentials.resolve_secret(
        "CONTENTFUL_ACCESS_TOKEN",
        "contentful",
        env_file=".secrets/custom-contentful.env",
    ) == "file-token"
    assert credentials.resolve_secret("CONTENTFUL_ACCESS_TOKEN", "contentful") == "env-token"

    monkeypatch.delenv("CONTENTFUL_ACCESS_TOKEN")
    assert credentials.resolve_secret("CONTENTFUL_ACCESS_TOKEN", "contentful") == "default-token"


def test_provider_env_path_rejects_unknown_provider():
    with pytest.raises(ValueError, match="unsupported provider"):
        credentials.provider_env_path("unknown")
