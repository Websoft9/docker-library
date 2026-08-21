from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def _frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    assert len(parts) >= 3, f"{path}: missing frontmatter"
    body = parts[1]
    result = {}
    for line in body.splitlines():
        if line.startswith("name:"):
            result["name"] = line.split(":", 1)[1].strip()
        elif line.startswith("description:"):
            result["description"] = line.split(":", 1)[1].strip()
    return result


def test_skill_readme_list_matches_skill_directories():
    skill_dirs = sorted(path.name for path in (REPO_ROOT / "skills").iterdir() if path.is_dir())
    readme = (REPO_ROOT / "skills" / "README.md").read_text(encoding="utf-8")
    listed = re.findall(r"^- `([a-z0-9-]+)`$", readme, flags=re.MULTILINE)

    assert sorted(listed) == skill_dirs


def test_each_skill_has_valid_frontmatter_and_supporting_files():
    for skill_dir in sorted(path for path in (REPO_ROOT / "skills").iterdir() if path.is_dir()):
        skill_path = skill_dir / "SKILL.md"
        assert skill_path.exists(), f"{skill_dir}: missing SKILL.md"

        frontmatter = _frontmatter(skill_path)
        assert frontmatter.get("name") == skill_dir.name
        assert SKILL_NAME_RE.match(frontmatter["name"]), f"{skill_path}: invalid skill name"
        assert isinstance(frontmatter.get("description"), str) and frontmatter["description"].strip(), f"{skill_path}: missing description"

        text = skill_path.read_text(encoding="utf-8")
        for ref in re.findall(r"docs/ai-sdlc/[A-Za-z0-9_.-]+", text):
            assert (REPO_ROOT / ref).exists(), f"{skill_path}: missing referenced doc {ref}"

        for filename in re.findall(r"- `?([A-Za-z0-9_.-]+\.md)`?$", text, flags=re.MULTILINE):
            if filename == "SKILL.md":
                continue
            assert (skill_dir / filename).exists(), f"{skill_path}: missing supporting file {filename}"


def test_no_skill_checklist_uses_interactive_make_cli():
    for path in sorted((REPO_ROOT / "skills").glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        assert "`make cli`" not in text, f"{path}: should not instruct interactive make cli"


def test_each_skill_has_required_sections_and_description_length_limit():
    for skill_path in sorted((REPO_ROOT / "skills").glob("*/SKILL.md")):
        text = skill_path.read_text(encoding="utf-8")

        for section in ("## Inputs", "## Output", "## Rules"):
            assert section in text, f"{skill_path}: missing section {section}"

        description = _frontmatter(skill_path).get("description", "")
        assert 1 <= len(description) <= 1024, f"{skill_path}: description length out of bounds"


def test_each_report_template_anchors_to_gate_vocabulary():
    gate_anchors = (
        "## Automated Checks",
        "## Owner E2E Focus",
        "## Owner Attention Points",
        "## Blocking Points",
    )
    for template_path in sorted((REPO_ROOT / "skills").glob("*/report-template.md")):
        text = template_path.read_text(encoding="utf-8")
        assert any(anchor in text for anchor in gate_anchors), f"{template_path}: no gate anchor section"
