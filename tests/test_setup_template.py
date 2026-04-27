"""Tests for setup_template helpers."""

from __future__ import annotations

from pathlib import Path

import setup_template


def test_render_template_path_replaces_placeholders() -> None:
    rendered = setup_template.render_template_path(
        Path("infra/hetzner/templates/{{PROJECT_NAME}}.service.j2"),
        {"PROJECT_NAME": "demo"},
    )

    assert rendered == Path("infra/hetzner/templates/demo.service.j2")


def test_ensure_claude_symlink_recreates_expected_symlink(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("agent guidance", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("stale file", encoding="utf-8")

    assert setup_template.ensure_claude_symlink(tmp_path) is True
    assert (tmp_path / "CLAUDE.md").is_symlink()
    assert (tmp_path / "CLAUDE.md").resolve() == (tmp_path / "AGENTS.md")
