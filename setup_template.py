#!/usr/bin/env python3
"""Interactive script to configure the Python project template.

This script prompts for template variable values and replaces all
{{VARIABLE_NAME}} placeholders in the project files.

Usage:
    python setup_template.py
"""

import datetime
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterator, List, Optional

# Template variables with their defaults and descriptions
TEMPLATE_VARS: Dict[str, Dict[str, str]] = {
    "PROJECT_NAME": {
        "default": "my-python-project",
        "description": "Project name (used for repository and package)",
    },
    "PROJECT_DESCRIPTION": {
        "default": "A Python project",
        "description": "Short project description (one line)",
    },
    "GITHUB_OWNER": {
        "default": "your-username",
        "description": "GitHub username or organization",
    },
    "MIN_PYTHON_VERSION": {
        "default": "3.10",
        "description": "Minimum Python version supported",
    },
    "PYTHON_VERSIONS": {
        "default": "3.10, 3.11, 3.12",
        "description": "Python versions for CI matrix (comma-separated)",
    },
    "MAX_LINE_LENGTH": {
        "default": "127",
        "description": "Maximum line length for code",
    },
    "MAX_COMPLEXITY": {
        "default": "10",
        "description": "Maximum cyclomatic complexity",
    },
    "COVERAGE_THRESHOLD": {
        "default": "95",
        "description": "Minimum test coverage percentage",
    },
    "SOURCE_DIR": {
        "default": "src",
        "description": "Source code directory name",
    },
    "TEST_DIR": {
        "default": "tests",
        "description": "Test directory name",
    },
    "MAIN_BRANCH": {
        "default": "main",
        "description": "Main branch name",
    },
    "DEV_BRANCH": {
        "default": "develop",
        "description": "Development branch name",
    },
    "CI_RUNNER": {
        "default": "github_hosted",
        "description": "Default CI runner target (github_hosted, self_hosted_linux, self_hosted_linux_arm64)",
    },
    "YEAR": {
        "default": str(datetime.date.today().year),
        "description": "Copyright year (used in LICENSE)",
    },
}

# Directories to skip entirely when scanning for template files.
SKIP_DIRS: set[str] = {
    ".git",
    "venv",
    ".venv",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    "htmlcov",
    ".tox",
}

# File extensions that are definitely binary — skip without trying.
BINARY_SUFFIXES: set[str] = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".pyc",
    ".pyo",
    ".so",
    ".dylib",
    ".exe",
    ".bin",
}

# Directories that may need renaming
DIRECTORIES_TO_RENAME: List[str] = ["src", "tests"]


def get_input(prompt: str, default: str) -> str:
    """Get user input with a default value.

    Args:
        prompt: The prompt to display.
        default: The default value if user presses Enter.

    Returns:
        User input or default value.
    """
    result = input(f"{prompt} [{default}]: ").strip()
    return result if result else default


def collect_variables() -> Dict[str, str]:
    """Collect all template variable values from user.

    Returns:
        Dictionary of variable names to values.
    """
    print("\n" + "=" * 60)
    print("Python Project Template Setup")
    print("=" * 60)
    print("\nPlease provide values for the following settings.")
    print("Press Enter to accept the default value shown in brackets.\n")

    values: Dict[str, str] = {}

    for var_name, var_info in TEMPLATE_VARS.items():
        print(f"\n{var_info['description']}")
        values[var_name] = get_input(f"  {var_name}", var_info["default"])

    return values


def replace_in_file(file_path: Path, replacements: Dict[str, str]) -> bool:
    """Replace template variables in a file.

    Args:
        file_path: Path to the file to process.
        replacements: Dictionary of variable names to values.

    Returns:
        True if file was modified, False otherwise.
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        original_content = content

        for var_name, value in replacements.items():
            pattern = "{{" + var_name + "}}"
            content = content.replace(pattern, value)
            assignment_pattern = (
                r"^(?P<prefix>\s*[^#\n=]+=\s*)(?P<current>[^#\n]+?)\s*#\s*TEMPLATE_VAR:"
                rf"{re.escape(var_name)}(?P<newline>\n?)$"
            )
            content = re.sub(
                assignment_pattern,
                lambda match: f"{match.group('prefix')}{value}{match.group('newline')}",
                content,
                flags=re.MULTILINE,
            )

        content = render_template_assignment_markers(content, replacements)

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  Warning: Could not process {file_path}: {e}")
        return False


def render_template_assignment_markers(content: str, replacements: Dict[str, str]) -> str:
    """Render standalone template markers that apply to the next assignment line."""
    rendered_lines: List[str] = []
    pending_var: Optional[str] = None

    for line in content.splitlines(keepends=True):
        stripped = line.strip()
        if stripped.startswith("# TEMPLATE_VAR:"):
            pending_var = stripped.removeprefix("# TEMPLATE_VAR:").strip()
            continue

        if pending_var is not None:
            value = replacements.get(pending_var)
            assignment = re.match(r"(?P<prefix>\s*[^#\n=]+=\s*)(?P<current>.*?)(?P<newline>\n?)$", line)
            if assignment is not None and value is not None:
                rendered_lines.append(f"{assignment.group('prefix')}{value}{assignment.group('newline')}")
            else:
                rendered_lines.append(line)
            pending_var = None
            continue

        rendered_lines.append(line)

    return "".join(rendered_lines)


def iter_all_template_files(project_root: Path, skip_self: Path) -> Iterator[Path]:
    """Walk the full project tree and yield candidate text files.

    Skips generated/venv directories and known binary file types. Every other
    file is yielded and processed by replace_in_file, which gracefully ignores
    files that cannot be decoded as UTF-8 or contain no template variables.
    This avoids the fragile manually-maintained FILES_TO_PROCESS list.
    """
    for file_path in sorted(project_root.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.resolve() == skip_self.resolve():
            continue
        rel = file_path.relative_to(project_root)
        # Skip files inside ignored directories (check all parent parts).
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if file_path.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield file_path


def check_remaining_placeholders(project_root: Path, skip_self: Path) -> List[str]:
    """Return a list of warning lines for any surviving {{...}} placeholders."""
    pattern = re.compile(r"\{\{[A-Z][A-Z0-9_]+\}\}")
    warnings: List[str] = []
    for file_path in iter_all_template_files(project_root, skip_self):
        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception:
            continue
        matches = sorted(set(pattern.findall(content)))
        if matches:
            rel = file_path.relative_to(project_root)
            warnings.append(f"  {rel}: {', '.join(matches)}")
    return warnings


def rename_directory(project_root: Path, old_name: str, new_name: str) -> Optional[Path]:
    """Rename a directory if the new name is different.

    Args:
        project_root: Root directory of the project.
        old_name: Current directory name.
        new_name: New directory name.

    Returns:
        New path if renamed, None otherwise.
    """
    if old_name == new_name:
        return None

    old_path = project_root / old_name
    new_path = project_root / new_name

    if old_path.exists():
        if new_path.exists():
            print(f"  Warning: Cannot rename {old_name} to {new_name}: target exists")
            return None
        shutil.move(str(old_path), str(new_path))
        return new_path
    return None


def update_file_references(project_root: Path, old_name: str, new_name: str) -> None:
    """Update references to renamed directories in files.

    Args:
        project_root: Root directory of the project.
        old_name: Old directory name.
        new_name: New directory name.
    """
    if old_name == new_name:
        return

    # Update file paths in the FILES_TO_PROCESS list pattern
    patterns = [
        (f"{old_name}/", f"{new_name}/"),
        (f"^{old_name}/", f"{new_name}/"),
        (f'"{old_name}"', f'"{new_name}"'),
        (f"'{old_name}'", f"'{new_name}'"),
    ]

    for file_path in project_root.rglob("*"):
        if file_path.is_file() and not file_path.name.startswith("."):
            try:
                content = file_path.read_text(encoding="utf-8")
                modified = False
                for old_pattern, new_pattern in patterns:
                    if old_pattern in content:
                        content = content.replace(old_pattern, new_pattern)
                        modified = True
                if modified:
                    file_path.write_text(content, encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                pass


def render_template_path(path: Path, replacements: Dict[str, str]) -> Path:
    """Render template placeholders in a relative path."""
    rendered = str(path)
    for var_name, value in replacements.items():
        rendered = rendered.replace("{{" + var_name + "}}", value)
    return Path(rendered)


def rename_template_paths(project_root: Path, replacements: Dict[str, str]) -> int:
    """Rename files and directories whose paths still contain template placeholders."""
    renamed_count = 0
    paths = sorted(
        project_root.rglob("*"),
        key=lambda candidate: len(candidate.relative_to(project_root).parts),
        reverse=True,
    )

    for path in paths:
        if not path.exists():
            continue
        relative_path = path.relative_to(project_root)
        rendered_relative_path = render_template_path(relative_path, replacements)
        if rendered_relative_path == relative_path:
            continue

        target_path = project_root / rendered_relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists() and path.is_dir() and not any(path.iterdir()):
            path.rmdir()
            continue
        path.rename(target_path)
        renamed_count += 1

    return renamed_count


def ensure_claude_symlink(project_root: Path) -> bool:
    """Ensure CLAUDE.md is a symlink to AGENTS.md."""
    agents_path = project_root / "AGENTS.md"
    claude_path = project_root / "CLAUDE.md"

    if not agents_path.exists():
        print("  Warning: AGENTS.md is missing; cannot recreate CLAUDE.md symlink")
        return False

    if claude_path.is_symlink():
        if os.readlink(claude_path) == "AGENTS.md":
            return True
        claude_path.unlink()
    elif claude_path.exists():
        claude_path.unlink()

    try:
        claude_path.symlink_to("AGENTS.md")
    except OSError as exc:
        print(f"  Warning: Could not create CLAUDE.md symlink: {exc}")
        return False

    return claude_path.is_symlink() and os.readlink(claude_path) == "AGENTS.md"


def init_git_repo(project_root: Path) -> bool:
    """Initialize a git repository.

    Args:
        project_root: Root directory of the project.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(
            ["git", "init"],
            cwd=project_root,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def install_pre_commit(project_root: Path) -> bool:
    """Install pre-commit hooks.

    Args:
        project_root: Root directory of the project.

    Returns:
        True if successful, False otherwise.
    """
    try:
        subprocess.run(
            ["pre-commit", "install"],
            cwd=project_root,
            capture_output=True,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def setup_branch_protection(project_root: Path, github_owner: str, project_name: str, main_branch: str) -> bool:
    """Configure branch protection rules via GitHub API.

    Args:
        project_root: Root directory of the project.
        github_owner: GitHub username or organization.
        project_name: Repository name.
        main_branch: Name of the main branch.

    Returns:
        True if successful, False otherwise.
    """
    # Check if gh CLI is available
    try:
        subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            check=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("  Warning: GitHub CLI not authenticated or not installed")
        print("  Run 'gh auth login' first, then run:")
        print("  ./scripts/github/setup-branch-protection.sh")
        return False

    config_file = project_root / "scripts" / "github" / "branch-protection-config.json"
    if not config_file.exists():
        print(f"  Warning: Config file not found: {config_file}")
        return False

    repo = f"{github_owner}/{project_name}"
    print(f"  Applying branch protection to {repo}:{main_branch}...")

    try:
        subprocess.run(
            [
                "gh",
                "api",
                "-X",
                "PUT",
                f"/repos/{repo}/branches/{main_branch}/protection",
                "--input",
                str(config_file),
            ],
            capture_output=True,
            check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print("  Warning: Failed to apply branch protection")
        print(f"  Error: {e.stderr.decode() if e.stderr else 'Unknown error'}")
        print("  You can apply it manually later with:")
        print("  ./scripts/github/setup-branch-protection.sh")
        return False


def main() -> int:  # noqa: C901 - setup flow is intentionally linear and prompt-driven.
    """Main entry point.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    # Determine project root (directory containing this script)
    project_root = Path(__file__).parent.resolve()

    # Collect variable values
    values = collect_variables()

    print("\n" + "=" * 60)
    print("Applying configuration...")
    print("=" * 60)

    # Process all template files by walking the full project tree.
    modified_count = 0
    script_path = Path(__file__)
    for file_path in iter_all_template_files(project_root, script_path):
        if replace_in_file(file_path, values):
            print(f"  Updated: {file_path.relative_to(project_root)}")
            modified_count += 1

    print(f"\n  Modified {modified_count} files")

    # Rename directories if needed
    if values["SOURCE_DIR"] != "src":
        if rename_directory(project_root, "src", values["SOURCE_DIR"]):
            print(f"  Renamed: src -> {values['SOURCE_DIR']}")
            update_file_references(project_root, "src", values["SOURCE_DIR"])

    if values["TEST_DIR"] != "tests":
        if rename_directory(project_root, "tests", values["TEST_DIR"]):
            print(f"  Renamed: tests -> {values['TEST_DIR']}")
            update_file_references(project_root, "tests", values["TEST_DIR"])

    renamed_template_paths = rename_template_paths(project_root, values)
    if renamed_template_paths:
        print(f"  Rendered {renamed_template_paths} template path(s)")

    if ensure_claude_symlink(project_root):
        print("  Ensured: CLAUDE.md -> AGENTS.md")
    else:
        print("  Warning: CLAUDE.md is not a symlink to AGENTS.md after setup")

    # Warn about any surviving {{...}} placeholders.
    remaining = check_remaining_placeholders(project_root, script_path)
    if remaining:
        print("\n  Warning: unreplaced placeholders found in:")
        for line in remaining:
            print(line)
        print("  These may be GitHub Actions expressions (OK) or missing template vars.")

    # Optional: Initialize git repository
    print("\n" + "-" * 60)
    init_git = get_input("Initialize git repository?", "yes")
    if init_git.lower() in ("yes", "y"):
        if init_git_repo(project_root):
            print("  Initialized git repository")
        else:
            print("  Warning: Could not initialize git repository")

    # Optional: Install pre-commit hooks
    install_hooks = get_input("Install pre-commit hooks?", "yes")
    if install_hooks.lower() in ("yes", "y"):
        if install_pre_commit(project_root):
            print("  Installed pre-commit hooks")
        else:
            print("  Warning: Could not install pre-commit hooks")
            print("  Run 'pip install pre-commit && pre-commit install' manually")

    # Optional: Setup branch protection (requires GitHub repo to exist first)
    print("\n" + "-" * 60)
    print("Branch protection requires the GitHub repository to exist.")
    setup_protection = get_input("Setup branch protection now?", "no")
    if setup_protection.lower() in ("yes", "y"):
        if setup_branch_protection(
            project_root,
            values["GITHUB_OWNER"],
            values["PROJECT_NAME"],
            values["MAIN_BRANCH"],
        ):
            print("  Branch protection configured successfully!")
        else:
            print("  You can set it up later by running:")
            print("  ./scripts/github/setup-branch-protection.sh")

    # Remove this setup script
    print("\n" + "-" * 60)
    remove_script = get_input("Remove this setup script?", "yes")
    if remove_script.lower() in ("yes", "y"):
        script_path = Path(__file__)
        script_path.unlink()
        print("  Removed setup_template.py")

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print(f"\nYour project '{values['PROJECT_NAME']}' is ready.")
    print("\nNext steps:")
    print("  1. Review the generated files")
    print("  2. Install dependencies: pip install -r requirements-dev.txt")
    print("  3. Run tests: pytest")
    print("  4. Deploy project-specific AI skills: ./scripts/deploy_ai_skills.sh")
    print("  5. Start coding!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
