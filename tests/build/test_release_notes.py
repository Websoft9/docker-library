import pytest

from _helpers import REPO_ROOT, load_build_module


notes = load_build_module("release_notes_test", REPO_ROOT / "ci/scripts/release_notes.py")


def test_release_changelog_preserves_human_notes_and_replaces_itself():
    body = "# Human introduction\n\nImportant installation notes.\n"
    merged = notes.merge_notes(body, "## Changes\n- First update")
    merged += "\nHuman follow-up below generated notes.\n"
    updated = notes.merge_notes(merged, "## Changes\n- Corrected update")
    assert updated.startswith(body.rstrip())
    assert updated.endswith("Human follow-up below generated notes.\n")
    assert "First update" not in updated
    assert updated.count(notes.START) == 1
    assert notes.merge_notes(updated, "## Changes\n- Corrected update") == updated


def test_release_changelog_rejects_broken_markers():
    with pytest.raises(ValueError, match="Invalid"):
        notes.merge_notes("Manual introduction\n" + notes.START, "Changes")
