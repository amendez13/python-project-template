# {{PROJECT_NAME}}

![CI](https://github.com/{{GITHUB_OWNER}}/{{PROJECT_NAME}}/workflows/CI/badge.svg)
![Python](https://img.shields.io/badge/python-{{MIN_PYTHON_VERSION}}+-blue.svg)
![Coverage](https://img.shields.io/badge/coverage-{{COVERAGE_THRESHOLD}}%25-green.svg)

{{PROJECT_DESCRIPTION}}

## Features

- Feature 1: Description
- Feature 2: Description
- Feature 3: Description

## Quick Start

### Prerequisites

- Python {{MIN_PYTHON_VERSION}} or higher
- pip (Python package installer)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/{{GITHUB_OWNER}}/{{PROJECT_NAME}}.git
cd {{PROJECT_NAME}}
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate   # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the application:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config/config.yaml with your settings
```

### Usage

```bash
# Run the application
python -m {{SOURCE_DIR}}.main
```

## Configuration

Configuration is stored in `config/config.yaml`. See `config/config.example.yaml` for all available options.

```yaml
# Example configuration
app:
  debug: false
  log_level: INFO

# Add your configuration sections here
```

## Project Structure

```
{{PROJECT_NAME}}/
├── .github/workflows/    # CI/CD configuration
├── .claude/              # Claude Code configuration
├── config/               # Configuration files
├── docs/                 # Documentation
├── {{SOURCE_DIR}}/       # Source code
├── {{TEST_DIR}}/         # Test files
├── CLAUDE.md             # AI assistant guidance
├── README.md             # This file
├── pyproject.toml        # Tool configuration
└── requirements.txt      # Dependencies
```

## Development

### Setup Development Environment

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov={{SOURCE_DIR}} --cov-report=term-missing
```

### Code Quality

This project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **bandit** for security scanning
- **pip-audit** for dependency vulnerability checking

All checks run automatically via pre-commit hooks and CI.

## CI/CD

GitHub Actions runs the following checks on every push and PR:

1. **Lint**: Black, isort, flake8, mypy
2. **Test**: pytest across Python {{PYTHON_VERSIONS}}
3. **Coverage**: {{COVERAGE_THRESHOLD}}% minimum coverage
4. **Security**: bandit and pip-audit

See [docs/CI.md](docs/CI.md) for details.

## Documentation

- [Documentation Index](docs/INDEX.md) - All documentation
- [Setup Guide](docs/SETUP.md) - Installation and configuration
- [CI Documentation](docs/CI.md) - CI/CD pipeline details

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

[Choose your license]

## Acknowledgments

- [Acknowledgment 1]
- [Acknowledgment 2]
