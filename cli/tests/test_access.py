from __future__ import annotations

import json

import pytest

from libs.access import access_metadata, safe_access_path


GROUP_KEYS = {
    "id", "service", "port", "protocol", "public", "requireDomain", "requireHttps",
    "rootUrl", "host", "mappedPort", "endpoints",
}
ENDPOINT_KEYS = {"roles", "scheme", "path", "query"}


def endpoint(**changes):
    return {"roles": ["web"], "scheme": "http", **changes}


def entry(**changes):
    endpoint_changes = {key: changes.pop(key) for key in list(changes) if key in ENDPOINT_KEYS}
    endpoints = changes.pop("endpoints", [endpoint(**endpoint_changes)])
    return {"id": "web", "service": "app", "port": 80, "public": True, **changes, "endpoints": endpoints}


def check(app_factory, groups, **kwargs):
    kwargs.setdefault("compose", "services:\n  app:\n    ports: ['9001:80']\n")
    target = app_factory("demo", variables={"access": groups}, **kwargs)
    return access_metadata(target)


def test_access_array_and_derived_kinds(app_factory):
    result = check(app_factory, [entry(roles=["web", "admin", "api", "db"])])
    assert result["ok"] is True
    assert result["entries"][0]["kinds"] == ["ui", "api", "infra"]
    assert result["entries"][0]["port_evidence"] == "matched"


@pytest.mark.parametrize("scheme", ["grpc", "grpcs"])
def test_database_grpc_is_an_infrastructure_connection(app_factory, scheme):
    result = check(app_factory, [entry(roles=["db"], scheme=scheme)])
    assert result["ok"] is True
    assert result["entries"][0]["kinds"] == ["infra"]


@pytest.mark.parametrize("changes", [
    {"roles": []}, {"roles": ["web", "web"]}, {"roles": ["api", "web"]},
    {"roles": ["unknown"]}, {"scheme": "unknown"}, {"scheme": "grpc"},
    {"primary": False}, {"id": "Bad_ID"}, {"service": "missing"}, {"port": True},
    {"port": 81}, {"port": "${MISSING}"}, {"port": "${PORT:-80}"},
    {"query": {"TOKEN": "do-not-leak"}}, {"query": {"safe": "${SECRET}"}},
    {"query": {"safe": "bad\nvalue"}}, {"unexpected": True},
])
def test_invalid_access(app_factory, changes):
    result = check(app_factory, [entry(**changes)])
    assert result["ok"] is False
    assert result["status"] == "invalid"
    assert "do-not-leak" not in json.dumps(result)


@pytest.mark.parametrize("path", ["//evil.example", "/../admin", "/%2e%2e/admin", "/%2fhost", "/bad%", "/bad%0a", "/\\host", "/?token=x", "https://host/"])
def test_unsafe_paths(path):
    assert safe_access_path(path) is False


@pytest.mark.parametrize("path", ["/", "/admin/", "/my%20page", "/%E4%B8%AD", "/a%3Fb"])
def test_safe_paths(path):
    assert safe_access_path(path) is True


def test_empty_unknown_and_legacy(app_factory):
    assert check(app_factory, [], compose="services: {}\n")["status"] == "no_entries"
    assert check(app_factory, [])["status"] == "invalid"
    result = access_metadata(app_factory("unknown", variables={}, declare_access=False))
    assert result["status"] == "not_declared"
    assert result["ok"] is False
    assert result["errors"]
    assert access_metadata(app_factory("legacy", variables={"access": {"web": {"port": 80}}}))["ok"] is False


def test_missing_access_blocks_gate_full_check_and_report(app_factory):
    from typer.testing import CliRunner
    from libs.main import app
    from libs.validate import check_app

    app_factory("unknown", variables={}, declare_access=False)
    assert check_app("unknown", gate="access")["ok"] is False
    assert check_app("unknown")["ok"] is False
    result = CliRunner().invoke(app, ["app-report", "--app", "unknown", "--json"])
    assert result.exit_code != 0
    assert json.loads(result.stdout)["automated_checks"]["access_metadata"]["ok"] is False


def test_group_and_endpoint_target_uniqueness(app_factory):
    assert check(app_factory, [entry(), entry(id="other")])["ok"] is False
    assert check(app_factory, [entry(endpoints=[endpoint(), endpoint()])])["ok"] is False
    assert check(app_factory, [entry(endpoints=[endpoint(), endpoint(path="/admin")])])["ok"] is True


def test_variable_port_and_unverified_evidence(app_factory, monkeypatch):
    monkeypatch.setenv("PORT", "9999")
    target = app_factory("variable", env="PORT='2222'\n", compose="services:\n  app:\n    ports: ['9000:${PORT}']\n",
                         variables={"access": [entry(port="${PORT}", roles=["ssh"], scheme="ssh")]})
    assert access_metadata(target)["entries"][0]["container_port"] == 2222
    target = app_factory("unverified", compose="services:\n  app: {}\n", variables={"access": [entry()]})
    result = access_metadata(target)
    assert result["ok"] is True
    assert result["status"] == "unverified"
    assert result["warnings"]


def test_missing_or_invalid_dictionary_fails_without_leaking(repo_fixture, app_factory):
    target = app_factory("dict", variables={"access": [entry()]})
    dictionary = repo_fixture / "metadata" / "access-types.json"
    dictionary.write_text('{"roles": {"secret": "do-not-leak"}}', encoding="utf-8")
    assert "do-not-leak" not in json.dumps(access_metadata(target))
    assert access_metadata(target)["ok"] is False
    dictionary.unlink()
    assert access_metadata(target)["ok"] is False


def test_access_gate_and_app_info_share_the_contract(app_factory):
    from libs.app import collect_app_info
    from libs.validate import check_app

    app_factory("valid", compose="services:\n  app:\n    ports: ['9001:80']\n", variables={"access": [entry(roles=["web", "api"])]})
    result = check_app("valid")
    assert result["ok"] is True
    assert result["access_metadata"]["status"] == "ok"
    info = collect_app_info("valid")
    assert info["access_metadata"] == result["access_metadata"]
    assert info["kinds"] == ["ui", "api"]
    app_factory("invalid", variables={"access": [entry(service="missing")]})
    assert check_app("invalid", gate="access")["ok"] is False
    assert check_app("invalid")["ok"] is False
    assert collect_app_info("invalid")["access"] is None


def test_cli_report_and_access_gate_expose_failures(app_factory):
    from typer.testing import CliRunner
    from libs import main

    app_factory("invalid", variables={"access": [entry(service="missing")]})
    runner = CliRunner()
    result = runner.invoke(main.app, ["app-check", "--app", "invalid", "--gate", "access", "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["result"]["status"] == "invalid"
    result = runner.invoke(main.app, ["app-report", "--app", "invalid", "--json"])
    assert result.exit_code == 1
    assert json.loads(result.stdout)["automated_checks"]["access_metadata"]["ok"] is False


def test_dictionary_and_native_role_examples(app_factory):
    from libs.repo import repo_path
    from libs.access import load_access_types

    schema = json.loads(repo_path("metadata", "variables.schema.json").read_text(encoding="utf-8"))
    dictionary = load_access_types(schema)
    assert len(dictionary["roles"]) == 11
    assert len(dictionary["schemes"]) == 19
    assert check(app_factory, [entry(roles=["api", "db"])])["ok"] is True
    assert check(app_factory, [entry(roles=["web", "gateway"])])["ok"] is True


def test_same_port_in_another_service_cannot_validate_target(app_factory):
    target = app_factory("foreign", compose="services:\n  app:\n    expose: [81]\n  foreign:\n    expose: [80]\n",
                         variables={"access": [entry()]})
    assert access_metadata(target)["ok"] is False


def test_dictionary_change_drives_validation_without_schema_enum(app_factory, repo_fixture):
    path = repo_fixture / "metadata" / "access-types.json"
    dictionary = json.loads(path.read_text(encoding="utf-8"))
    dictionary["roles"]["custom"] = {"kind": "api", "schemes": ["http"], "description": "Custom purpose."}
    path.write_text(json.dumps(dictionary), encoding="utf-8")
    assert check(app_factory, [entry(roles=["custom"])])["ok"] is True


def test_malformed_compose_services_returns_a_safe_error(app_factory):
    target = app_factory("malformed", compose="services: [invalid]\n", variables={"access": [entry()]})
    assert access_metadata(target)["status"] == "invalid"


@pytest.mark.parametrize("ports", [80, "80", {"target": 80}])
def test_malformed_service_ports_do_not_crash_validation(app_factory, ports):
    compose = json.dumps({"services": {"app": {"ports": ports}}})
    target = app_factory("malformed", compose=compose, variables={"access": [entry()]})
    assert access_metadata(target)["status"] == "invalid"


def test_unbounded_port_variable_returns_a_safe_error(app_factory):
    target = app_factory("malformed", env="APP_PORT=" + "9" * 5000 + "\n", variables={"access": [entry(port="${APP_PORT}")]})
    assert access_metadata(target)["status"] == "invalid"


def test_query_order_and_default_path_do_not_create_duplicate_targets(app_factory):
    first = entry(query={"a": "1", "b": "2"})
    second = entry(id="other", path="/", query={"b": "2", "a": "1"})
    assert check(app_factory, [first, second])["ok"] is False


def test_public_is_a_platform_policy_not_a_compose_mirror(app_factory):
    """``public`` states the platform default; upstream compose keeps its own mappings."""
    published = "services:\n  app:\n    ports: ['9001:80']\n"
    unpublished = "services:\n  app:\n    expose: [80]\n"
    assert check(app_factory, [entry()], compose=published)["ok"] is True
    assert check(app_factory, [entry(public=False)], compose=published)["ok"] is True
    assert check(app_factory, [entry()], compose=unpublished)["ok"] is True
    assert check(app_factory, [entry(public=False)], compose=unpublished)["ok"] is True


def test_published_media_needs_a_matching_exemption(app_factory):
    compose = "services:\n  app:\n    ports: ['9001:80']\n  media:\n    ports: ['10000:10000/udp']\n"
    assert check(app_factory, [entry()], compose=compose)["ok"] is False
    valid = compose + "    x-websoft9-unmanaged-ports: {'10000/udp': 'WebRTC media'}\n"
    assert check(app_factory, [entry()], compose=valid)["ok"] is True
    assert check(app_factory, [entry()], compose=valid.replace("10000/udp': 'WebRTC", "10000/tcp': 'WebRTC"))["ok"] is False


def test_udp_and_tcp_on_the_same_port_are_distinct_groups(app_factory):
    compose = "services:\n  app:\n    ports: ['5140:5140/tcp', '5140:5140/udp']\n"
    groups = [
        entry(id="syslog-tcp", port=5140),
        entry(id="syslog-udp", port=5140, protocol="udp"),
    ]
    assert check(app_factory, groups, compose=compose)["ok"] is True


def test_value_fields_require_url_endpoint_and_declared_env(app_factory):
    assert check(app_factory, [entry(rootUrl=["APP_URL"])])["ok"] is False
    assert check(app_factory, [entry(rootUrl=["APP_URL"], protocol="udp")], compose="services:\n  app:\n    ports: ['9001:80/udp']\n")["ok"] is False
    assert check(app_factory, [entry(rootUrl=["APP_URL"])], env="APP_URL=http://localhost:9001\n")["ok"] is True
    assert check(
        app_factory,
        [entry(rootUrl=["APP_URL"]), entry(id="api", port=81, service="api", rootUrl=["APP_URL"])],
        env="APP_URL=http://localhost:9001\n",
        compose="services:\n  app:\n    ports: ['9001:80']\n  api:\n    ports: ['9002:81']\n",
    )["ok"] is False


def test_require_domain_and_https_need_a_url_endpoint(app_factory):
    assert check(app_factory, [entry(requireDomain=True)])["ok"] is True
    assert check(app_factory, [entry(requireHttps=True)])["ok"] is False
    assert check(
        app_factory, [entry(requireHttps=True, public=False)], compose="services:\n  app:\n    expose: [80]\n"
    )["ok"] is True
    assert check(app_factory, [entry(requireDomain=True, requireHttps=True, scheme="https")], env="")["ok"] is True
    assert check(
        app_factory,
        [entry(requireDomain=True, endpoints=[endpoint(roles=["ssh"], scheme="ssh")])],
        compose="services:\n  app:\n    ports: ['9001:80']\n",
    )["ok"] is False


def test_deprecated_entries_object_is_rejected(app_factory):
    legacy = {"entries": [
        {"id": "web", "roles": ["web"], "primary": True, "service": "app", "port": 80, "scheme": "http", "path": "/"},
    ]}
    target = app_factory("demo", compose="services:\n  app:\n    ports: ['9001:80']\n", variables={"access": legacy})
    result = access_metadata(target)
    assert result["ok"] is False
    assert result["status"] == "invalid"


def test_restore_rejects_unused_old_access_before_moving(app_factory, repo_fixture):
    from libs.app import restore_app

    source = app_factory("retired", archived=True, variables={"access": {"web": {"port": 80}}})
    with pytest.raises(ValueError, match="Invalid access metadata"):
        restore_app("retired")
    assert source.is_dir()
    assert not (repo_fixture / "apps" / "retired").exists()


def test_restore_rejects_missing_access_before_moving(app_factory, repo_fixture):
    from libs.app import restore_app

    source = app_factory("retired", archived=True, declare_access=False)
    with pytest.raises(ValueError, match="Invalid access metadata"):
        restore_app("retired")
    assert source.is_dir()
    assert not (repo_fixture / "apps" / "retired").exists()


def test_restore_preserves_valid_access_metadata(app_factory):
    from libs.app import restore_app

    app_factory("retired", archived=True, compose="services:\n  app:\n    ports: ['9001:80']\n", variables={"access": [entry()]})
    assert restore_app("retired", dry_run=True)["access_metadata"]["status"] == "ok"


def test_v2_rejects_deprecated_w9_residuals_across_env_compose_and_src(app_factory, repo_fixture):
    from libs.validate import check_app

    (repo_fixture / "i18n" / "translation.json").write_text('{"W9_DEEPSEEK_API_KEY_SET": ["", ""]}\n', encoding="utf-8")
    clean = app_factory(
        "clean",
        env="W9_ID=clean\nW9_VERSION=1.0\nW9_DEEPSEEK_API_KEY_SET=''\n",
        compose="services:\n  app:\n    ports: ['9001:80']\n",
        variables={"name": "clean", "trademark": "Clean", "release": True, "edition": [{"dist": "community", "version": ["1.0"]}], "access": [entry()]},
    )
    assert check_app("clean")["ok"] is True

    dirty_env = app_factory("dirty-env", env="W9_ID=dirty\nW9_HTTP_PORT_SET=9001\n", compose="services:\n  app:\n    ports: ['9001:80']\n", variables={"access": [entry()]})
    assert access_metadata(dirty_env)["ok"] is False

    dirty_compose = app_factory("dirty-compose", env="W9_ID=dirty\n", compose="services:\n  app:\n    environment:\n      URL: ${W9_URL}\n    ports: ['9001:80']\n", variables={"access": [entry()]})
    assert access_metadata(dirty_compose)["ok"] is False

    dirty_src = app_factory("dirty-src", env="W9_ID=dirty\n", compose="services:\n  app:\n    ports: ['9001:80']\n", variables={"access": [entry()]})
    (dirty_src / "src").mkdir(exist_ok=True)
    (dirty_src / "src" / "hook.php").write_text("<?php $u = getenv('W9_URL');\n", encoding="utf-8")
    assert access_metadata(dirty_src)["ok"] is False


def test_v2_rejects_w9_target_vars_profile_or_init_services_and_hostname_wiring(app_factory):
    assert check(app_factory, [entry(rootUrl=["W9_CUSTOM_URL"])], env="W9_ID=demo\nW9_CUSTOM_URL=http://localhost\n")["ok"] is False
    assert check(
        app_factory,
        [entry()],
        compose="services:\n  app:\n    profiles: ['gpu']\n    ports: ['9001:80']\n",
    )["ok"] is False
    assert check(
        app_factory,
        [entry()],
        compose="services:\n  app:\n    restart: 'no'\n    ports: ['9001:80']\n",
    )["ok"] is False
    assert check(
        app_factory,
        [entry(host=["APP_HOST"])],
        env="W9_ID=demo\nAPP_HOST=app.example.com\n",
        compose="services:\n  app:\n    hostname: '${APP_HOST}'\n    ports: ['9001:80']\n",
    )["ok"] is False


def test_shared_dictionary_and_documented_access_examples_validate():
    import re
    import jsonschema
    from pathlib import Path
    from libs.access import load_access_types

    root = Path(__file__).resolve().parents[2]
    schema = json.loads((root / "metadata" / "variables.schema.json").read_text(encoding="utf-8"))
    definitions = load_access_types(schema)
    assert len(definitions["roles"]) == 11
    assert len(definitions["schemes"]) == 19
    validator = jsonschema.Draft202012Validator({"$defs": schema["$defs"], **schema["properties"]["access"]})
    for filename in ("app-access-spec.md", "upstream-spec.md"):
        text = (root / "docs" / filename).read_text(encoding="utf-8")
        examples = [json.loads(block) for block in re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL)]
        declarations = [example for example in examples if isinstance(example, dict) and "access" in example]
        assert declarations
        for example in declarations:
            validator.validate(example["access"])