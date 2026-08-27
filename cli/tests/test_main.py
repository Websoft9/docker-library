from __future__ import annotations

import typer

from libs import main


class DummyApp:
    def __init__(self):
        self.registered_commands = []

    def __call__(self):
        raise FileNotFoundError("repo missing")


class DummyParent:
    def get_help(self):
        return "HELP TEXT"


class DummyContext:
    parent = DummyParent()


def test_help_command_prints_parent_help(monkeypatch):
    output = []
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.help_command(DummyContext())

    assert output == [
        ("HELP TEXT", False),
        ("\nLocal by default; remote-aware commands read defaults from .secrets/remote.env (TARGET, SSH_HOST, SSH_USER, SSH_SECRET_PATH, DEPLOY_ROOT). Current remote-aware commands: app-deploy, app-down, app-tests, appstore-sync, appstore-deploy.", False),
    ]


def test_proxy_command_calls_save_clear_and_show(monkeypatch):
    calls = []
    output = []
    monkeypatch.setattr(main.http, "save_proxy", lambda value: calls.append(("save", value)))
    monkeypatch.setattr(main.http, "clear_proxy", lambda: calls.append(("clear", None)))
    monkeypatch.setattr(main.http, "detect_proxy", lambda: "detected-proxy")
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    main.proxy_command(set_url="http://proxy", clear=False)
    main.proxy_command(set_url=None, clear=True)
    main.proxy_command(set_url=None, clear=False)

    assert calls == [("save", "http://proxy"), ("clear", None)]
    assert output == [
        ("saved proxy: http://proxy", False),
        ("saved proxy removed", False),
        ("detected-proxy", False),
    ]


def test_run_returns_exit_code_4_on_repository_error(monkeypatch):
    output = []
    monkeypatch.setattr(main, "app", DummyApp())
    monkeypatch.setattr(typer, "echo", lambda message, err=False: output.append((message, err)))

    assert main.run() == 4
    assert output == [("repo missing", True)]
