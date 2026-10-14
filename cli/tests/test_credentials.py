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


def test_load_provider_env_supports_dockerhub(repo_fixture):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dockerhub.env").write_text(
        "DOCKERHUB_USERNAME=user\nDOCKERHUB_TOKEN=token\n",
        encoding="utf-8",
    )

    data = credentials.load_provider_env("dockerhub")

    assert data["DOCKERHUB_USERNAME"] == "user"
    assert data["DOCKERHUB_TOKEN"] == "token"


def test_load_provider_env_supports_dns(repo_fixture):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "dns.env").write_text(
        "DNS_PROVIDER=aliyun\nDNS_KEY_ID=id\nDNS_KEY_SECRET=secret\nDNS_DOMAIN=libs.websoft9.cn\n",
        encoding="utf-8",
    )

    data = credentials.load_provider_env("dns")

    assert data["DNS_DOMAIN"] == "libs.websoft9.cn"
    assert data["DNS_PROVIDER"] == "aliyun"
    assert credentials.provider_env_path("dns").name == "dns.env"


def test_load_provider_env_supports_cloud_providers(repo_fixture):
    (repo_fixture / ".secrets").mkdir(exist_ok=True)
    (repo_fixture / ".secrets" / "aws.env").write_text(
        "AWS_ACCESS_KEY_ID=id\nAWS_SECRET_ACCESS_KEY=secret\nAWS_REGION=us-east-1\n",
        encoding="utf-8",
    )

    data = credentials.load_provider_env("aws")

    assert data["AWS_REGION"] == "us-east-1"
    assert credentials.provider_env_path("aws").name == "aws.env"
    assert credentials.provider_env_path("aliyun").name == "aliyun.env"
    assert credentials.provider_env_path("azure").name == "azure.env"


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
