from __future__ import annotations

from jinja2 import Environment, FileSystemLoader

from libs.metadata import app_dir
from libs.repo import repo_path

TEMPLATE_ROOT = repo_path("metadata", "templates")


def render_readme(app_name: str) -> dict:
    target = app_dir(app_name)
    if not target:
        raise FileNotFoundError(app_name)

    variables_path = target / "variables.json"
    if not variables_path.exists():
        raise FileNotFoundError(f"{app_name}/variables.json")

    import json

    variables = json.loads(variables_path.read_text(encoding="utf-8"))
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_ROOT)), keep_trailing_newline=True)
    rendered = env.get_template("readme.jinja2").render(**variables)

    readme_path = target / "README.md"
    readme_path.write_text(rendered, encoding="utf-8")

    return {
        "app": app_name,
        "path": str(readme_path.relative_to(repo_path())),
        "bytes": len(rendered.encode("utf-8")),
    }
