from __future__ import annotations

import json

import pytest

from libs import validate


@pytest.mark.parametrize("entry,env,expected", [
    ("9001:${W9_HTTP_PORT}", {"W9_HTTP_PORT": "80"}, 80),
    ("9001:$W9_HTTP_PORT/tcp", {"W9_HTTP_PORT": "80"}, 80),
    ({"target": "${W9_HTTP_PORT}", "published": "9001"}, {"W9_HTTP_PORT": "80"}, 80),
    ("127.0.0.1:9001:80/udp", {}, 80),
    (80, {}, 80),
    ({"target": 80}, {}, 80),
    ("9001:${MISSING}", {}, None),
    ("9001:${W9_HTTP_PORT}", {"W9_HTTP_PORT": "invalid"}, None),
    ("9001:${W9_HTTP_PORT}", {"W9_HTTP_PORT": None}, None),
    (True, {}, None),
    ({"target": False}, {}, None),
    ("${HOST_PORT:-9001}:${NGINX_PORT:-80}", {}, 80),
    ("9001:${NGINX_PORT:-80}", {"NGINX_PORT": ""}, 80),
    ("9001:${NGINX_PORT:-80}", {"NGINX_PORT": "8080"}, 8080),
    ("9001:${NGINX_PORT-80}", {}, 80),
    ("9001:${NGINX_PORT-80}", {"NGINX_PORT": ""}, None),
    ({"target": "${NGINX_PORT:-80}"}, {}, 80),
])
def test_container_port_resolves_project_environment_only(entry, env, expected):
    assert validate._container_port(entry, env) == expected


def test_access_ports_resolve_quoted_project_values_not_shell_environment(app_factory, monkeypatch):
    monkeypatch.setenv("W9_HTTP_PORT", "9999")
    target = app_factory("ports", env="W9_HTTP_PORT='80'\nW9_HTTP_PORT_SET=9001\n", compose=(
        "services:\n  web:\n    ports:\n      - '${W9_HTTP_PORT_SET}:${W9_HTTP_PORT}'\n"
    ), variables={"access": {"web": {"port": 80}}})
    result = validate._policy_result(target)
    assert result["access_ports_ok"] is True
    assert result["access_missing_ports"] == []


@pytest.mark.parametrize("database,status", [
    (None, "not_applicable"),
    ([], "ok"),
    ({"type": "postgresql", "supported_modes": ["bundled", "external"], "bundled": {"service": "db"}}, "legacy"),
])
def test_database_contract_support_does_not_require_app_migration(app_factory, database, status):
    from libs.app import collect_app_info

    app_factory("unmigrated", compose="services:\n  db:\n    image: postgres:17\n", variables={} if database is None else {"database": database})
    result = validate.check_app("unmigrated")
    assert result["ok"] is True
    assert result["database_metadata"]["status"] == status
    info = collect_app_info("unmigrated")
    assert info["database_connections"] == []
    assert info["database_metadata"]["status"] == status
    assert info["database"] == info["database_lifecycle"]


def test_database_metadata_accepts_partial_sources_without_resolving_credentials(app_factory):
    target = app_factory("demo", compose="services:\n  db:\n    image: postgres:17\n", variables={
        "database": [{"id": "rds", "providers": [
            {"type": "internal", "service": "db", "driver": "postgresql"},
            {"type": "external", "drivers": ["postgresql"]},
        ], "datasource": {"DATABASE_URL": "postgres://${users[*].user}:${users[*].password}@${host}:${port}/${name}"},
            "users": [{"user": "${MISSING_USER}", "password": "", "usage": ["application"]}]}],
    })
    result = validate.check_app("demo", gate="all")
    assert result["database_metadata"]["status"] == "ok"
    assert result["ok"] is True


@pytest.mark.parametrize("database", [
    [{"id": "rds", "providers": [{"type": "internal", "service": "missing", "driver": "postgresql"}]}],
    [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "not-an-engine"}]}],
    [{"id": "rds", "providers": [{"type": "external", "drivers": ["sqlite"]}], "datasource": {"URL": "${url}"}}],
    [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
      "datasource": {"DATABASE_URL": "${users[*].wrong}"}}],
        [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
            "datasource": {"DATABASE_URL": "${}"}}],
        [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
            "datasource": {"DATABASE_URL": "${host"}}],
        [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}],
            "datasource": {"DATABASE_URL": "${host}${port}${}"}}],
    [{"id": "rds", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}]}] * 2,
    [{"id": "first", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}]},
     {"id": "second", "providers": [{"type": "internal", "service": "db", "driver": "postgresql"}]}],
    [{"id": "rds", "providers": [{"type": "external", "drivers": ["postgresql"]}]}],
])
def test_invalid_database_metadata_fails_actual_quality_gate(app_factory, database):
    app_factory("demo", compose="services:\n  db:\n    image: postgres:17\n", variables={"database": database})
    result = validate.check_app("demo")
    assert result["structure"]["ok"] is True
    assert result["policy"]["ok"] is True
    assert result["database_metadata"]["errors"]
    assert result["ok"] is False
    assert validate.check_app("demo", gate="database-metadata")["ok"] is False


def test_database_metadata_reports_missing_dictionary_and_redacts_values(repo_fixture, app_factory):
    app_factory("demo", variables={"database": [{"id": "rds", "providers": [
        {"type": "external", "drivers": ["postgresql"]}], "datasource": {"URL": "${url}"}}]})
    (repo_fixture / "metadata" / "database-types.json").unlink()
    assert validate.check_app("demo")["database_metadata"]["ok"] is False
    target = app_factory("bad", variables={"database": [{"users": [{"password": "sensitive-value"}]}]})
    result = validate._database_metadata_result(target)
    assert result["ok"] is False
    assert "sensitive-value" not in json.dumps(result)


def test_readiness_report_exposes_database_metadata_failure(app_factory):
    from typer.testing import CliRunner
    from libs import main

    app_factory("demo", variables={"database": [{"id": "rds", "providers": [
        {"type": "external", "drivers": ["not-an-engine"]}], "datasource": {"URL": "${url}"}}]})
    result = CliRunner().invoke(main.app, ["app-report", "--app", "demo", "--json"])
    assert result.exit_code == 1
    report = json.loads(result.stdout)
    assert report["decision"] == "blocked"
    assert report["automated_checks"]["database_metadata"]["ok"] is False


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
    assert result["url_declared_ok"] is False
    assert result["url_replace_ok"] is False
    assert result["url_replace_required"] is False
    assert result["url_replace_required_ok"] is True


def test_policy_result_requires_url_replace_when_app_url_uses_w9_url(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env=(
            "W9_URL=appname.example.com\n"
            "W9_URL_REPLACE=false\n"
            "APP_URL=http://${W9_URL}\n"
        ),
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["url_declared_ok"] is True
    assert result["url_replace_required"] is True
    assert result["url_replace_required_ok"] is False


def test_policy_result_accepts_url_replace_for_app_url(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env=(
            "W9_URL=appname.example.com\n"
            "W9_URL_REPLACE=true\n"
            "ROOT_URL=http://${W9_URL}\n"
        ),
    )

    result = validate._policy_result(app_path)

    assert result["url_replace_required"] is True
    assert result["url_replace_required_ok"] is True


def test_policy_result_accepts_braced_url_replace_form(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env=(
            "W9_URL=appname.example.com\n"
            "W9_URL_REPLACE=true\n"
            "ROOT_URL=http://${W9_URL}\n"
        ),
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is True
    assert result["url_replace_required"] is True
    assert result["url_replace_required_ok"] is True
    assert result["url_replace_ok"] is True


def test_policy_result_rejects_hard_pinned_dependency_patch_tag(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  redis:\n"
            "    image: redis:7.0.7\n"
        ),
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["dependency_tag_policy_ok"] is False
    assert result["dependency_patch_tags"] == [{"service": "redis", "image": "redis:7.0.7"}]


def test_policy_result_allows_variable_or_two_segment_dependency_tags(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  db:\n"
            "    image: postgres:${W9_DB_VERSION}\n"
            "  redis:\n"
            "    image: redis:7.0\n"
        ),
        env="W9_DB_VERSION=15\n",
    )

    result = validate._policy_result(app_path)

    assert result["dependency_tag_policy_ok"] is True
    assert result["dependency_patch_tags"] == []


def test_policy_result_flags_access_port_missing_from_compose(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  web:\n"
            "    ports:\n"
            '      - "${W9_HTTP_PORT_SET}:8080"\n'
        ),
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "access": {"web": {"port": 8080}, "admin": {"port": 3000}},
        },
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["access_ports_ok"] is False
    assert result["access_missing_ports"] == [{"key": "admin", "port": 3000}]


def test_policy_result_accepts_access_port_present_in_compose(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  web:\n"
            "    ports:\n"
            '      - "${W9_HTTP_PORT_SET}:3080"\n'
            "  admin:\n"
            "    ports:\n"
            '      - "${W9_ADMIN_GUI_PORT_SET}:3000"\n'
        ),
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "access": {"web": {"port": 3080}, "admin": {"port": 3000}},
        },
    )

    result = validate._policy_result(app_path)

    assert result["access_ports_ok"] is True
    assert result["access_missing_ports"] == []


def test_policy_result_requires_declared_secrets_present_and_non_empty(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env="APP_KEY=secretvalue\nEMPTY_KEY=\n",
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "env": {"secrets": ["APP_KEY", "MISSING_KEY", "EMPTY_KEY"]},
        },
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["secrets_ok"] is False
    assert result["secrets_declared"] == ["APP_KEY", "MISSING_KEY", "EMPTY_KEY"]
    assert result["secrets_missing"] == ["MISSING_KEY"]
    assert result["secrets_empty"] == ["EMPTY_KEY"]


def test_policy_result_accepts_declared_secrets_with_values(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        env="APP_KEY=secretvalue\nOH_KEY=anothervalue\n",
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "env": {"secrets": ["APP_KEY", "OH_KEY"]},
        },
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is True
    assert result["secrets_ok"] is True
    assert result["secrets_missing"] == []
    assert result["secrets_empty"] == []


@pytest.mark.parametrize("template,valid", [
    ("AbC123" * 6, True),
    ("a1" * 32, True),
    ("sk-" + "a1" * 32, True),
    ("1234-45687-12312", True),
    ("CHANGE_ME", False),
    ("a1" * 4, False),
    ("string:" + "a1" * 16, False),
    ("YWJjZGVmZ2hpamtsbW5vcA==", False),
    ("eyJhbGc.eyJzdWI.signature", False),
    ("123e4567-e89b-12d3-a456-426614174000", False),
    ("prefix-1234567890123456", False),
])
def test_secret_template_format_contract(template, valid):
    from libs.secret_audit import template_issue

    assert (template_issue(template) is None) == valid


@pytest.mark.parametrize("env,valid", [
    ("SEED=" + "a1" * 32 + "\nKEY=string:${SEED}\n", True),
    ("KEY=${W9_POWER_PASSWORD}\nW9_POWER_PASSWORD=\n", True),
    ("KEY=${MISSING}\n", False),
    ("KEY=${SEED}\nSEED=${KEY}\n", False),
    ("KEY=${SEED:-fallback}\n", False),
    ("KEY=\n", False),
])
def test_secret_gate_validates_references(repo_fixture, app_factory, env, valid):
    from libs.secret_audit import check_secret_templates

    target = app_factory("demo", env=env, variables={"env": {"secrets": ["KEY"]}})
    result = check_secret_templates(target)
    assert result["ok"] == valid
    assert "a1" * 32 not in json.dumps(result)


def test_ckan_secret_gate_preserves_shared_signing_seed():
    from pathlib import Path
    from dotenv import dotenv_values
    from libs.secret_audit import check_secret_templates

    target = Path(__file__).resolve().parents[2] / "apps" / "ckan"
    result = check_secret_templates(target)
    values = dotenv_values(target / ".env", interpolate=False)
    assert result["ok"]
    assert values["CKAN___API_TOKEN__JWT__ENCODE__SECRET"] == "string:${CKAN_API_TOKEN_SECRET}"
    assert values["CKAN___API_TOKEN__JWT__DECODE__SECRET"] == "${CKAN___API_TOKEN__JWT__ENCODE__SECRET}"
    declared = json.loads((target / "variables.json").read_text())["env"]["secrets"]
    assert set(declared) == {"CKAN___BEAKER__SESSION__SECRET", "CKAN_API_TOKEN_SECRET"}


def test_secret_gate_is_exposed_by_app_check(repo_fixture, app_factory):
    app_factory("demo", env="KEY=" + "a1" * 32 + "\n", variables={"env": {"secrets": ["KEY"]}})
    payload = validate.check_app("demo", gate="secrets")
    assert payload["gate"] == "secrets"
    assert payload["ok"]
    assert payload["result"]["fields"] == [{"name": "KEY", "kind": "random_template", "references": []}]


def test_policy_result_flags_invalid_setup_access_service_and_duplicate_ids(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  app:\n"
            "    ports:\n"
            '      - "${W9_HTTP_PORT_SET}:8080"\n'
        ),
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "access": {"web": {"port": 8080, "path": "/"}},
            "setup": {
                "steps": [
                    {
                        "id": "setup-token",
                        "text": "Read logs.",
                        "action": {"type": "show-log", "service": "missing", "tail": 50},
                    },
                    {
                        "id": "setup-token",
                        "text": "Open setup.",
                        "action": {"type": "open", "access": "admin", "path": "/setup"},
                    },
                ]
            },
        },
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is False
    assert result["setup_ok"] is False
    assert result["setup_missing_services"] == [{"step": "setup-token", "service": "missing"}]
    assert result["setup_missing_access"] == [{"step": "setup-token", "access": "admin"}]
    assert result["setup_duplicate_ids"] == ["setup-token"]


def test_policy_result_accepts_valid_setup_steps(repo_fixture, app_factory):
    app_path = app_factory(
        "demo",
        compose=(
            "services:\n"
            "  app:\n"
            "    ports:\n"
            '      - "${W9_HTTP_PORT_SET}:8080"\n'
        ),
        variables={
            "name": "demo",
            "trademark": "Demo",
            "release": True,
            "edition": [{"dist": "community", "version": ["1.0"]}],
            "requirements": {"cpu": "1", "memory": "1", "disk": "1"},
            "access": {"web": {"port": 8080, "path": "/"}},
            "setup": {
                "steps": [
                    {
                        "id": "setup-token",
                        "text": "Read logs.",
                        "action": {"type": "show-log", "service": "app", "tail": 50},
                    },
                    {
                        "id": "setup-wizard",
                        "text": "Open setup.",
                        "action": {"type": "open", "access": "web", "path": "/setup"},
                    },
                ]
            },
        },
    )

    result = validate._policy_result(app_path)

    assert result["ok"] is True
    assert result["setup_ok"] is True
    assert result["setup_missing_services"] == []
    assert result["setup_missing_access"] == []
    assert result["setup_duplicate_ids"] == []


def test_check_app_returns_gate_specific_payload(repo_fixture, app_factory):
    app_factory("demo")

    structure = validate.check_app("demo", gate="structure")
    policy = validate.check_app("demo", gate="policy")
    all_result = validate.check_app("demo", gate="all")

    assert structure["gate"] == "structure"
    assert policy["gate"] == "policy"
    assert all_result["ok"] is True


def test_database_result_flags_eol_bundled_database(repo_fixture, app_factory):
    (repo_fixture / "metadata" / "db-lifecycle.json").write_text(
        json.dumps({
            "version": 1,
            "engines": {
                "mysql": {
                    "tracks": [
                        {"version": "8.4", "track": "lts", "eol": "2032-04-30"},
                        {"version": "8.0", "track": "lts", "eol": "2026-04-30"},
                    ]
                }
            },
        }),
        encoding="utf-8",
    )
    app_path = app_factory(
        "demo",
        env="W9_DB_VERSION=8.0\n",
        compose="services:\n  db:\n    image: mysql:${W9_DB_VERSION}\n",
    )

    result = validate._database_result(app_path)

    assert result["ok"] is False
    assert result["status"] == "eol"
    assert result["databases"][0]["engine"] == "mysql"
    assert result["databases"][0]["current"] == "8.0"


def test_database_gate_accepts_alive_lts(repo_fixture, app_factory):
    (repo_fixture / "metadata" / "db-lifecycle.json").write_text(
        json.dumps({
            "version": 1,
            "engines": {
                "mysql": {"tracks": [{"version": "8.4", "track": "lts", "eol": "2032-04-30"}]}
            },
        }),
        encoding="utf-8",
    )
    app_factory(
        "demo",
        env="W9_DB_VERSION=8.4\n",
        compose="services:\n  db:\n    image: mysql:${W9_DB_VERSION}\n",
    )

    payload = validate.check_app("demo", gate="database")

    assert payload["ok"] is True
    assert payload["result"]["status"] == "ok"
