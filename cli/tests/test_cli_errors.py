from __future__ import annotations

from typer.testing import CliRunner

from libs import main


runner = CliRunner()


def test_info_and_archive_return_exit_code_4_for_missing_app(repo_fixture):
    info_result = runner.invoke(main.app, ["app-info", "--app", "missing", "--json"])
    archive_result = runner.invoke(main.app, ["app-archive", "--app", "missing", "--json"])

    assert info_result.exit_code == 4
    assert archive_result.exit_code == 4


def test_report_returns_exit_code_1_when_checks_block(monkeypatch):
    monkeypatch.setattr(main.validate, "check_app", lambda app_name, gate="all": {"ok": False, "structure": {}, "policy": {}})

    result = runner.invoke(main.app, ["app-report", "--app", "demo", "--json"])

    assert result.exit_code == 1


def test_restore_returns_usage_error_when_target_already_exists(repo_fixture, app_factory):
    app_factory("demo")
    app_factory("demo", archived=True)

    result = runner.invoke(main.app, ["app-restore", "--app", "demo", "--json"])

    assert result.exit_code == 2
    assert "already exists" in (result.stdout + getattr(result, "stderr", ""))
