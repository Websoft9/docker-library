from __future__ import annotations

import typer

from libs.output import print_output


def test_print_output_emits_plain_string(monkeypatch):
    output = []
    monkeypatch.setattr(typer, "echo", lambda message: output.append(message))

    print_output("hello", as_json=False)

    assert output == ["hello"]


def test_print_output_emits_json_for_non_string_payload(monkeypatch):
    output = []
    monkeypatch.setattr(typer, "echo", lambda message: output.append(message))

    print_output({"ok": True}, as_json=False)
    print_output({"ok": True}, as_json=True)

    assert output == ['{\n  "ok": true\n}', '{\n  "ok": true\n}']
