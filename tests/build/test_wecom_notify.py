from __future__ import annotations

import io
import json
import urllib.error

import pytest
import yaml

from _helpers import REPO_ROOT, load_build_module

notify = load_build_module("wecom_notify_test", REPO_ROOT / "ci/scripts/wecom_notify.py")


def test_release_summary_preserves_links_and_utf8_limit():
    message = notify.release_message(
        "Websoft9/docker-library", "0.8.4", "https://github.com/org/repo/releases/tag/0.8.4",
        "https://github.com/org/repo/actions/runs/123", "<!-- generated-changelog:start -->\n" + "中文变更\n" * 2000,
    )
    assert len(message.encode("utf-8")) <= 4096
    assert "0.8.4" in message and "中文变更" in message
    assert "generated-changelog" not in message
    assert "releases/tag/0.8.4" in message
    assert "library-latest.zip" in message
    assert "actions/runs/123" in message
    assert message.endswith("…（内容已截断，完整说明见 Release）")


def test_sender_posts_markdown_and_checks_business_error(monkeypatch, capsys):
    calls = []

    def post(request, timeout):
        calls.append(request)
        assert timeout == 2
        return io.BytesIO(json.dumps({"errcode": 45009 if len(calls) == 1 else 0}).encode())

    monkeypatch.setattr(notify.urllib.request, "urlopen", post)
    monkeypatch.setattr(notify.time, "sleep", lambda seconds: None)
    assert notify.send_markdown("发布成功", "https://example.com/webhook?key=secret") is True
    assert len(calls) == 2
    assert json.loads(calls[-1].data) == {"msgtype": "markdown", "markdown": {"content": "发布成功"}}
    assert "secret" not in capsys.readouterr().out


@pytest.mark.parametrize("failure", ["network", "business", "invalid-json"])
def test_failed_notifications_are_bounded_and_do_not_leak_webhook(monkeypatch, capsys, failure):
    calls = []

    def post(*args, **kwargs):
        calls.append(args)
        if failure == "network":
            raise urllib.error.URLError("https://example.com/?key=secret")
        return io.BytesIO(b'{"errcode":40014,"errmsg":"secret"}' if failure == "business" else b"not json")

    monkeypatch.setattr(notify.urllib.request, "urlopen", post)
    monkeypatch.setattr(notify.time, "sleep", lambda seconds: None)
    assert notify.send_markdown("test", "https://example.com/?key=secret") is False
    assert len(calls) == 3
    output = capsys.readouterr().out
    assert "::warning::" in output
    assert "secret" not in output


def test_missing_secret_skips_network(monkeypatch):
    monkeypatch.setattr(notify.urllib.request, "urlopen", lambda *a, **k: pytest.fail("unexpected network call"))
    assert notify.send_markdown("test", "") is False


def test_release_notification_is_last_success_only_and_reuses_scan_channel():
    workflow = yaml.safe_load((REPO_ROOT / ".github/workflows/appstore-publish.yml").read_text())
    steps = workflow["jobs"]["publish"]["steps"]
    step = steps[-1]
    assert steps[-2]["name"] == "Update published GitHub Release"
    assert step["if"] == "success() && steps.resolve_channel.outputs.channel == 'release'"
    assert step["continue-on-error"] is True
    assert step["env"]["WECOM_WEBHOOK"] == "${{ secrets.WECOM_WEBHOOK }}"
    assert "--release-notes-file release-notes.md" in step["run"]
    scan = yaml.safe_load((REPO_ROOT / ".github/workflows/maintenance-scan.yml").read_text())
    notifications = [step for job in scan["jobs"].values() for step in job.get("steps", [])
                     if step.get("name", "").startswith("Notify WeCom")]
    assert len(notifications) == 2
    assert all("ci/scripts/wecom_notify.py --markdown-file" in step["run"] for step in notifications)
