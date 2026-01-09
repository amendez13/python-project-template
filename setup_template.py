#!/usr/bin/env python3
"""Interactive script to configure the Python project template.

This script prompts for template variable values and replaces all
{{VARIABLE_NAME}} placeholders in the project files.

Usage:
    python setup_template.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


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
}

# Files to process (relative to project root)
FILES_TO_PROCESS: List[str] = [
    ".github/workflows/ci.yml",
    ".github/workflows/claude.yml",
    ".github/workflows/claude-code-review.yml",
    ".github/dependabot.yml",
    ".pre-commit-config.yaml",
    "pyproject.toml",
    ".flake8",
    ".pylintrc",
    "CLAUDE.md",
    "README.md",
    "docs/INDEX.md",
    "docs/CI.md",
    "docs/SETUP.md",
    "docs/ARCHITECTURE.md",
    "docs/planning/TASK_MANAGEMENT.md",
    "config/config.example.yaml",
    "src/__init__.py",
    "src/main.py",
    "tests/__init__.py",
    "tests/conftest.py",
    "tests/test_main.py",
]

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

        if content != original_content:
            file_path.write_text(content, encoding="utf-8")
            return True
        return False
    except Exception as e:
        print(f"  Warning: Could not process {file_path}: {e}")
        return False


def rename_directory(
    project_root: Path, old_name: str, new_name: str
) -> Optional[Path]:
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


def update_file_references(
    project_root: Path, old_name: str, new_name: str
) -> None:
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


def main() -> int:
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

    # Process all template files
    modified_count = 0
    for file_rel_path in FILES_TO_PROCESS:
        file_path = project_root / file_rel_path
        if file_path.exists():
            if replace_in_file(file_path, values):
                print(f"  Updated: {file_rel_path}")
                modified_count += 1
        else:
            # Try with new directory names
            new_path = file_rel_path
            if file_rel_path.startswith("src/"):
                new_path = file_rel_path.replace("src/", values["SOURCE_DIR"] + "/", 1)
            elif file_rel_path.startswith("tests/"):
                new_path = file_rel_path.replace(
                    "tests/", values["TEST_DIR"] + "/", 1
                )
            file_path = project_root / new_path
            if file_path.exists():
                if replace_in_file(file_path, values):
                    print(f"  Updated: {new_path}")
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
    print("  4. Start coding!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
