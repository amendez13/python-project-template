# Setup Guide

This guide walks you through setting up {{PROJECT_NAME}} for development or usage.

## Prerequisites

- Python {{MIN_PYTHON_VERSION}} or higher
- pip (Python package installer)
- git

### Optional

- [List optional dependencies]

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/{{GITHUB_OWNER}}/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

### 3. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Configure the Application

```bash
# Copy example configuration
cp config/config.example.yaml config/config.yaml

# Edit configuration with your settings
# On macOS/Linux:
nano config/config.yaml
# Or use your preferred editor
```

### 5. Verify Installation

```bash
# Run tests to verify setup
pytest

# Or run the application
python -m {{SOURCE_DIR}}.main --help
```

## Configuration

### config/config.yaml

The main configuration file. See `config/config.example.yaml` for all available options.

```yaml
# Application settings
app:
  debug: false
  log_level: INFO

# Add your configuration sections
```

### Environment Variables

You can also configure the application using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `APP_DEBUG` | Enable debug mode | `false` |
| `APP_LOG_LEVEL` | Logging level | `INFO` |

## Session Notes

This template treats session notes as committed project history, not private scratch files.

- Read [AGENTS.md](../AGENTS.md) for the delivery workflow rules that govern when notes should be updated.
- Read [notes/README.md](../notes/README.md) for the directory layout, note style, and the daily-note template.
- Daily notes live at `notes/YYYY/MM/YYYY-MM-DD.md`.
- If you want the optional secondary summary-log workflow, copy `notes/.notes-config.yaml.example` to `notes/.notes-config.yaml` and customize the paths for your environment.
- The canonical skill source for note automation lives at `ai-skills/session-notes/`. If you use the shared AI-skills deployment pattern, deploy that skill to your local agent harnesses after editing it.

## Development Setup

### Install Pre-commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Verify hooks work
pre-commit run --all-files
```

### Deploy AI Skills

The template ships canonical AI skill sources under `ai-skills/` and a deploy flow that renders them to both Claude and Codex:

```bash
./scripts/deploy_ai_skills.sh
```

Requirements:
- `ansible-playbook` installed locally
- write access to `~/.claude/skills/` and `~/.codex/skills/`

The deploy script renders:
- Claude skills to `~/.claude/skills/<name>/skill.md`
- Codex skills to `~/.codex/skills/<name>/SKILL.md`
- Codex interface metadata to `~/.codex/skills/<name>/agents/openai.yaml`

See [AI_SKILLS.md](AI_SKILLS.md) for the canonical source layout, starter skills, and troubleshooting guidance.

### IDE Setup

#### VS Code

Recommended extensions:
- Python
- Pylance
- Black Formatter
- isort

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "[python]": {
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

#### PyCharm

1. Set Python interpreter to `./venv/bin/python`
2. Enable Black formatter
3. Enable isort for imports

## Troubleshooting

### Common Issues

**Virtual environment not activated**
```bash
source venv/bin/activate
```

**Dependencies not installed**
```bash
pip install -r requirements.txt
```

**Pre-commit hooks not running**
```bash
pre-commit install
```

**Configuration file not found**
```bash
cp config/config.example.yaml config/config.yaml
```

### Getting Help

- Check the [Documentation Index](INDEX.md)
- Review [notes/README.md](../notes/README.md) for note conventions
- Review [CI documentation](CI.md) for testing issues
- Open an issue on GitHub
