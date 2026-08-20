from __future__ import annotations

import json
from typing import Any

import typer


def print_output(payload: Any, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
        return

    if isinstance(payload, str):
        typer.echo(payload)
        return

    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))
