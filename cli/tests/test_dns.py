from __future__ import annotations

import types

import pytest
from typer.testing import CliRunner

from libs import dns, main


runner = CliRunner()


def test_percent_encode_follows_aliyun_rules():
    assert dns.percent_encode("* .~/") == "%2A%20.~%2F"
    assert dns.percent_encode("A+=") == "A%2B%3D"


def test_sign_regression_vector():
    params = {
        "Action": "DescribeDomains",
        "Format": "JSON",
        "Version": "2015-01-09",
        "AccessKeyId": "testid",
        "SignatureMethod": "HMAC-SHA1",
        "SignatureVersion": "1.0",
        "SignatureNonce": "abc",
        "Timestamp": "2020-01-01T00:00:00Z",
    }

    assert dns.sign(params, "secret") == "yKnuUjPfe1LrSQiay1mvEM6hbIE="
    assert dns.sign(params, "secret") == dns.sign(params, "secret")
    assert dns.sign(params, "other") != dns.sign(params, "secret")


def test_wildcard_fqdn_prepends_and_preserves_star():
    assert dns.wildcard_fqdn("libs.websoft9.cn") == "*.libs.websoft9.cn"
    assert dns.wildcard_fqdn("*.libs.websoft9.cn") == "*.libs.websoft9.cn"
    assert dns.wildcard_fqdn("LIBs.Websoft9.CN.") == "*.libs.websoft9.cn"

    with pytest.raises(ValueError, match="domain is required"):
        dns.wildcard_fqdn("")


def test_resolve_zone_picks_longest_suffix():
    assert dns.resolve_zone("*.libs.websoft9.cn", ["websoft9.cn"]) == ("websoft9.cn", "*.libs")
    assert dns.resolve_zone("*.libs.websoft9.cn", ["websoft9.cn", "libs.websoft9.cn"]) == (
        "libs.websoft9.cn",
        "*",
    )
    assert dns.resolve_zone("websoft9.cn", ["websoft9.cn"]) == ("websoft9.cn", "@")

    with pytest.raises(dns.DnsError, match="not managed"):
        dns.resolve_zone("*.libs.example.com", ["websoft9.cn"])


def test_resolve_target_ip_local_and_overrides(monkeypatch):
    assert dns.resolve_target_ip(target="local") == "127.0.0.1"
    assert dns.resolve_target_ip(target="remote", ip="1.2.3.4") == "1.2.3.4"

    monkeypatch.setattr(dns.remote, "ssh_host", lambda value=None: "5.6.7.8")
    assert dns.resolve_target_ip(target="remote") == "5.6.7.8"

    with pytest.raises(ValueError, match="invalid target"):
        dns.resolve_target_ip(target="cloud")


def _stub(monkeypatch, records):
    calls = []
    monkeypatch.setattr(dns, "resolve_credentials", lambda *args, **kwargs: ("id", "secret"))
    monkeypatch.setattr(dns, "resolve_endpoint", lambda *args, **kwargs: dns.DEFAULT_ENDPOINT)
    monkeypatch.setattr(dns, "list_domains", lambda *args, **kwargs: ["websoft9.cn"])
    monkeypatch.setattr(dns, "find_records", lambda *args, **kwargs: records)

    def fake_call(action, params, *args, **kwargs):
        calls.append((action, params))
        return {"RecordId": "rec-1"}

    monkeypatch.setattr(dns, "call", fake_call)
    return calls


def test_bind_creates_when_missing(monkeypatch):
    calls = _stub(monkeypatch, [])

    payload = dns.bind("libs.websoft9.cn", "1.2.3.4")

    assert calls == [
        (
            "AddDomainRecord",
            {
                "DomainName": "websoft9.cn",
                "RR": "*.libs",
                "Type": "A",
                "Value": "1.2.3.4",
                "TTL": dns.DEFAULT_TTL,
                "Line": "default",
            },
        )
    ]
    assert payload["action"] == "created"
    assert payload["fqdn"] == "*.libs.websoft9.cn"
    assert payload["previous_value"] is None
    assert payload["record_id"] == "rec-1"


def test_bind_updates_existing_single_record(monkeypatch):
    existing = [{"RecordId": "old-1", "RR": "*.libs", "Type": "A", "Value": "9.9.9.9", "Line": "default"}]
    calls = _stub(monkeypatch, existing)

    payload = dns.bind("libs.websoft9.cn", "1.2.3.4")

    assert calls[0][0] == "UpdateDomainRecord"
    assert calls[0][1]["RecordId"] == "old-1"
    assert payload["action"] == "updated"
    assert payload["previous_value"] == "9.9.9.9"


def test_bind_unchanged_when_value_matches(monkeypatch):
    existing = [{"RecordId": "rec-1", "RR": "*.libs", "Type": "A", "Value": "1.2.3.4", "Line": "default"}]
    calls = _stub(monkeypatch, existing)

    payload = dns.bind("libs.websoft9.cn", "1.2.3.4")

    assert calls == []
    assert payload["action"] == "unchanged"
    assert payload["previous_value"] == "1.2.3.4"


def test_bind_recovers_from_duplicate_on_create(monkeypatch):
    state = {"records": []}
    monkeypatch.setattr(dns, "resolve_credentials", lambda *args, **kwargs: ("id", "secret"))
    monkeypatch.setattr(dns, "resolve_endpoint", lambda *args, **kwargs: dns.DEFAULT_ENDPOINT)
    monkeypatch.setattr(dns, "list_domains", lambda *args, **kwargs: ["websoft9.cn"])
    monkeypatch.setattr(dns, "find_records", lambda *args, **kwargs: list(state["records"]))

    def fake_call(action, params, *args, **kwargs):
        if action == "AddDomainRecord":
            state["records"] = [{"RecordId": "rec-1", "RR": "*.libs", "Type": "A", "Value": "1.2.3.4", "Line": "default"}]
            raise dns.DnsError("Aliyun DNS AddDomainRecord failed: DomainRecordDuplicate The DNS record already exists.")
        raise AssertionError(f"unexpected call: {action}")

    monkeypatch.setattr(dns, "call", fake_call)

    payload = dns.bind("libs.websoft9.cn", "1.2.3.4")

    assert payload["action"] == "unchanged"
    assert payload["record_id"] == "rec-1"


def test_bind_refuses_duplicate_records(monkeypatch):
    _stub(monkeypatch, [{"RecordId": "a"}, {"RecordId": "b"}])

    with pytest.raises(dns.DnsError, match="multiple"):
        dns.bind("libs.websoft9.cn", "1.2.3.4")


def test_delete_removes_the_single_record(monkeypatch):
    calls = _stub(monkeypatch, [{"RecordId": "rec-9", "RR": "*.libs", "Type": "A", "Value": "1.2.3.4"}])

    payload = dns.delete("libs.websoft9.cn")

    assert calls == [("DeleteDomainRecord", {"RecordId": "rec-9"})]
    assert payload["action"] == "deleted"
    assert payload["value"] == "1.2.3.4"


def test_delete_rejects_missing_and_multiple(monkeypatch):
    _stub(monkeypatch, [])
    with pytest.raises(dns.DnsError, match="no A record"):
        dns.delete("libs.websoft9.cn")

    _stub(monkeypatch, [{"RecordId": "a"}, {"RecordId": "b"}])
    with pytest.raises(dns.DnsError, match="refusing to delete"):
        dns.delete("libs.websoft9.cn")


def test_call_rejects_missing_credentials():
    with pytest.raises(dns.DnsError, match="missing Aliyun credentials"):
        dns.call("DescribeDomains", {}, "", "")


def test_call_raises_on_api_error(monkeypatch):
    class Response:
        status_code = 400
        reason = "Bad Request"

        def json(self):
            return {"Code": "InvalidAccessKeyId.NotFound", "Message": "specified access key is not found"}

    monkeypatch.setattr(dns.http, "get", lambda *args, **kwargs: Response())

    with pytest.raises(dns.DnsError, match="InvalidAccessKeyId"):
        dns.call("DescribeDomains", {}, "id", "secret")


def test_call_hints_dns_permission_for_ram_forbidden(monkeypatch):
    class Response:
        status_code = 403
        reason = "Forbidden"

        def json(self):
            return {"Code": "Forbidden.RAM", "Message": "User not authorized to operate on the specified resource, or this API doesn't support RAM."}

    monkeypatch.setattr(dns.http, "get", lambda *args, **kwargs: Response())

    with pytest.raises(dns.DnsError, match="AliyunDNSFullAccess"):
        dns.call("DescribeDomains", {}, "id", "secret")


def _ok(stdout: str = "", stderr: str = ""):
    return types.SimpleNamespace(returncode=0, stdout=stdout, stderr=stderr)


def test_configure_container_sets_wildcard_domain(monkeypatch):
    calls = []
    monkeypatch.setattr(dns.remote, "default_target", lambda: "local")
    monkeypatch.setattr(dns.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(dns, "_run_container", lambda command, ctx: (calls.append((command, ctx)) or _ok()))

    payload = dns.configure_container("libs.websoft9.cn")

    assert payload["status"] == "updated"
    assert payload["container"] == "websoft9"
    assert calls[0] == (["docker", "inspect", "websoft9"], None)
    assert calls[1][0] == [
        "docker",
        "exec",
        "websoft9",
        "websoft9",
        "setconfig",
        "--section",
        "domain",
        "--key",
        "wildcard_domain",
        "--value",
        "libs.websoft9.cn",
    ]


def test_configure_container_skips_when_missing(monkeypatch):
    monkeypatch.setattr(dns.remote, "default_target", lambda: "local")
    monkeypatch.setattr(dns.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(
        dns,
        "_run_container",
        lambda command, ctx: types.SimpleNamespace(returncode=1, stdout="", stderr="No such container"),
    )

    payload = dns.configure_container("libs.websoft9.cn")

    assert payload["status"] == "skipped"
    assert payload["reason"] == "container not found"


def test_configure_container_uses_remote_context(tmp_path, monkeypatch):
    secret = tmp_path / "default.pem"
    secret.write_text("key", encoding="utf-8")
    calls = []
    monkeypatch.setattr(dns.remote, "default_target", lambda: "remote")
    monkeypatch.setattr(dns.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(dns.remote, "ssh_host", lambda value=None: value or "1.2.3.4")
    monkeypatch.setattr(dns.remote, "ssh_user", lambda value=None: value or "root")
    monkeypatch.setattr(dns.remote, "resolve_secret_path", lambda value=None: secret)
    monkeypatch.setattr(dns, "_run_container", lambda command, ctx: (calls.append((command, ctx)) or _ok()))

    payload = dns.configure_container("libs.websoft9.cn")

    assert payload["status"] == "updated"
    assert calls[0][1] == ("1.2.3.4", "root", secret)


def test_configure_container_skips_without_remote_host(monkeypatch):
    monkeypatch.setattr(dns.remote, "default_target", lambda: "remote")
    monkeypatch.setattr(dns.remote, "appstore_container", lambda value=None: value or "websoft9")
    monkeypatch.setattr(dns.remote, "ssh_host", lambda value=None: value)

    payload = dns.configure_container("libs.websoft9.cn")

    assert payload["status"] == "skipped"
    assert payload["reason"] == "missing remote host"


def test_dns_bind_command_contract(repo_fixture, monkeypatch):
    captured = {}
    container = {}

    def fake_bind(**kwargs):
        captured.update(kwargs)
        return {"action": "created", "fqdn": "*.libs.websoft9.cn", "value": kwargs["value"]}

    def fake_configure(domain, **kwargs):
        container["domain"] = domain
        container["kwargs"] = kwargs
        return {"status": "updated", "container": "websoft9"}

    monkeypatch.setattr(main.dns, "bind", fake_bind)
    monkeypatch.setattr(main.dns, "configure_container", fake_configure)

    result = runner.invoke(
        main.app,
        ["dns-bind", "--domain", "libs.websoft9.cn", "--ip", "1.2.3.4", "--json"],
    )

    assert result.exit_code == 0
    assert captured["value"] == "1.2.3.4"
    assert captured["domain"] == "libs.websoft9.cn"
    assert container["domain"] == "libs.websoft9.cn"
    assert '"action": "created"' in result.stdout
    assert '"status": "updated"' in result.stdout


def test_dns_bind_command_skips_container_when_disabled(repo_fixture, monkeypatch):
    called = []
    monkeypatch.setattr(main.dns, "bind", lambda **kwargs: {"action": "created"})
    monkeypatch.setattr(main.dns, "configure_container", lambda *args, **kwargs: called.append(True) or {})

    result = runner.invoke(
        main.app,
        ["dns-bind", "--domain", "libs.websoft9.cn", "--ip", "1.2.3.4", "--no-container", "--json"],
    )

    assert result.exit_code == 0
    assert called == []
    assert "container_config" not in result.stdout


def test_dns_delete_command_requires_domain(repo_fixture):
    result = runner.invoke(main.app, ["dns-delete", "--json"])

    assert result.exit_code == 2
    assert "domain is required" in (result.stdout + result.stderr)
