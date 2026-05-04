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


def test_render_template_path_replaces_ai_skill_placeholders() -> None:
    rendered = setup_template.render_template_path(
        Path("ai-skills/{{PROJECT_NAME}}-feature-delivery/skill.yaml"),
        {"PROJECT_NAME": "gentle-site-visitor"},
    )

    assert rendered == Path("ai-skills/gentle-site-visitor-feature-delivery/skill.yaml")


def test_iter_additional_template_files_discovers_ai_skill_text_files(tmp_path: Path) -> None:
    skill_dir = tmp_path / "ai-skills" / "{{PROJECT_NAME}}-feature-delivery"
    skill_dir.mkdir(parents=True)
    skill_file = skill_dir / "skill.yaml"
    instruction_file = skill_dir / "instructions.md"
    binary_file = skill_dir / "icon.png"
    skill_file.write_text('name: "{{PROJECT_NAME}}-feature-delivery"', encoding="utf-8")
    instruction_file.write_text("# {{PROJECT_NAME}} Feature Delivery", encoding="utf-8")
    binary_file.write_bytes(b"not a template text file")

    discovered = {file_path.relative_to(tmp_path) for file_path in setup_template.iter_additional_template_files(tmp_path)}

    assert Path("ai-skills/{{PROJECT_NAME}}-feature-delivery/skill.yaml") in discovered
    assert Path("ai-skills/{{PROJECT_NAME}}-feature-delivery/instructions.md") in discovered
    assert Path("ai-skills/{{PROJECT_NAME}}-feature-delivery/icon.png") not in discovered


def test_rename_template_paths_renders_ai_skill_directories(tmp_path: Path) -> None:
    skill_dir = tmp_path / "ai-skills" / "{{PROJECT_NAME}}-feature-delivery"
    skill_dir.mkdir(parents=True)
    (skill_dir / "skill.yaml").write_text("name: demo", encoding="utf-8")

    renamed_count = setup_template.rename_template_paths(
        tmp_path,
        {"PROJECT_NAME": "gentle-site-visitor"},
    )

    assert renamed_count >= 1
    assert (tmp_path / "ai-skills" / "gentle-site-visitor-feature-delivery" / "skill.yaml").exists()
    assert not skill_dir.exists()


def test_ensure_claude_symlink_recreates_expected_symlink(tmp_path: Path) -> None:
    (tmp_path / "AGENTS.md").write_text("agent guidance", encoding="utf-8")
    (tmp_path / "CLAUDE.md").write_text("stale file", encoding="utf-8")

    assert setup_template.ensure_claude_symlink(tmp_path) is True
    assert (tmp_path / "CLAUDE.md").is_symlink()
    assert (tmp_path / "CLAUDE.md").resolve() == (tmp_path / "AGENTS.md")
