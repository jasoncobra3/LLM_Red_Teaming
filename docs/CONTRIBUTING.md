# Contributing Guidelines

Thank you for your interest in contributing to the LLM Red Teaming Platform! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Pull Request Process](#pull-request-process)
8. [Issue Reporting](#issue-reporting)
9. [Development Workflow](#development-workflow)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in all interactions.

### Expected Behavior

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Publishing others' private information
- Other conduct inappropriate in a professional setting

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- A GitHub account
- API keys for at least one LLM provider (OpenAI, Groq, etc.)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Red_Teaming.git
   cd Red_Teaming
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/Red_Teaming.git
   ```

## Development Setup

### 1. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=your_key_here
# GROQ_API_KEY=your_key_here
```

### 4. Initialize Database

```bash
python migrate_db.py
```

### 5. Run Application

```bash
# Streamlit UI
streamlit run app.py

# OR FastAPI
python web_app.py
```

## How to Contribute

### Types of Contributions

We welcome the following types of contributions:

1. **Bug Fixes**: Fix issues identified in the issue tracker
2. **New Features**: Add new functionality or capabilities
3. **Documentation**: Improve or add documentation
4. **Tests**: Add or improve test coverage
5. **Performance**: Optimize existing code
6. **UI/UX**: Enhance user interface and experience

### Finding Issues to Work On

- Check the [Issues](https://github.com/ORIGINAL_OWNER/Red_Teaming/issues) page
- Look for issues labeled `good first issue` for beginners
- Issues labeled `help wanted` are actively seeking contributors
- Comment on an issue to indicate you're working on it

### Creating New Issues

Before creating an issue:
1. Search existing issues to avoid duplicates
2. Use issue templates when available
3. Provide detailed information:
   - Clear description of the problem/feature
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (OS, Python version, etc.)
   - Relevant logs or screenshots

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://pep8.org/) with some modifications:

```python
# Use descriptive variable names
target_model = "gpt-4"  # Good
tm = "gpt-4"  # Bad

# Add docstrings to functions
def run_red_team_scan(target_model: str, attacker_model: str) -> dict:
    """
    Execute a red team security scan against a target LLM.
    
    Args:
        target_model: The model to test (e.g., "gpt-4")
        attacker_model: The model generating attacks (e.g., "gpt-3.5-turbo")
    
    Returns:
        dict: Scan results including scores and test cases
    """
    pass

# Use type hints
def extract_results(data: dict) -> list[dict]:
    return data.get("results", [])

# Keep functions focused and small
# Each function should do one thing well
```

### Code Organization

```
File Structure:
├── core/          # Business logic
├── ui/            # User interface components
├── database/      # Data models and DB operations
├── config/        # Configuration management
├── utils/         # Helper functions
├── auth/          # Authentication
└── reports/       # Report generation
```

### Naming Conventions

- **Files**: `snake_case.py` (e.g., `red_team_engine.py`)
- **Classes**: `PascalCase` (e.g., `LangChainAdapter`)
- **Functions**: `snake_case` (e.g., `run_red_team_scan`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `VULNERABILITIES`)
- **Private functions**: `_leading_underscore` (e.g., `_extract_test_case`)

### Import Order

```python
# 1. Standard library imports
import os
import sys
from typing import Any, Dict, List

# 2. Third-party imports
import streamlit as st
from langchain_core.messages import HumanMessage

# 3. Local application imports
from config.settings import settings
from core.llm_factory import create_deepeval_model
```

### Error Handling

```python
# Use specific exceptions
try:
    result = dangerous_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except Exception as e:
    logger.exception("Unexpected error occurred")
    return default_value

# Provide context in error messages
if not api_key:
    raise ValueError(
        "API key not found. Please set OPENAI_API_KEY in .env file"
    )
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information for debugging")
logger.info("General informational messages")
logger.warning("Warning messages for unexpected situations")
logger.error("Error messages for failures")

# Include context in logs
logger.info(f"Starting scan {scan_id} with target {target_model}")
```

## Testing Guidelines

### Writing Tests

```python
# tests/test_red_team_engine.py
import pytest
from core.red_team_engine import run_red_team_scan

def test_scan_with_valid_models():
    """Test scan execution with valid model configuration."""
    result = run_red_team_scan(
        scan_id="test-123",
        target_model="gpt-4",
        attacker_model="gpt-3.5-turbo",
        vulnerabilities=["Robustness"],
        attacks_per_vuln=1
    )
    
    assert result["status"] == "completed"
    assert result["total_tests"] > 0

def test_scan_with_invalid_model():
    """Test scan handling of invalid model name."""
    with pytest.raises(ValueError):
        run_red_team_scan(
            scan_id="test-124",
            target_model="invalid-model",
            attacker_model="gpt-3.5-turbo"
        )
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_red_team_engine.py

# Run with coverage
pytest --cov=core --cov-report=html
```

### Test Coverage

- Aim for >80% code coverage
- Focus on critical paths and edge cases
- Mock external API calls
- Test error handling

## Pull Request Process

### Before Submitting

1. **Update your fork**:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**:
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**:
   ```bash
   # Run tests
   pytest
   
   # Run the application
   streamlit run app.py
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add new vulnerability detection"
   ```

   **Commit Message Format**:
   ```
   <type>: <short description>
   
   <detailed description>
   
   <footer>
   ```
   
   Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Submitting the PR

1. Go to the original repository on GitHub
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:
   - **Title**: Clear, concise description
   - **Description**: What changes were made and why
   - **Related Issue**: Link to related issues (e.g., "Fixes #123")
   - **Testing**: How you tested the changes
   - **Screenshots**: If UI changes are involved

### PR Review Process

1. **Automated Checks**: CI/CD will run tests
2. **Code Review**: Maintainers will review your code
3. **Feedback**: Address any requested changes
4. **Approval**: Once approved, your PR will be merged

### After Your PR is Merged

1. Delete your feature branch (GitHub will prompt)
2. Update your local main branch:
   ```bash
   git checkout main
   git pull upstream main
   ```

## Issue Reporting

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. See error

**Expected behavior**
What you expected to happen.

**Screenshots**
Add screenshots if applicable.

**Environment:**
- OS: [e.g., Windows 11]
- Python version: [e.g., 3.10.5]
- Browser: [e.g., Chrome 120]

**Additional context**
Any other relevant information.
```

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How you envision this working.

**Alternatives**
Other approaches you've considered.

**Additional Context**
Any other relevant information.
```

## Development Workflow

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: New features
- `bugfix/*`: Bug fixes
- `hotfix/*`: Urgent production fixes

### Release Process

1. Create release branch from `develop`
2. Update version numbers
3. Update CHANGELOG.md
4. Test thoroughly
5. Merge to `main` and tag
6. Merge back to `develop`

## Questions?

- Check existing documentation
- Search closed issues
- Ask in discussions
- Contact maintainers

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Featured in project README (for significant contributions)

---

**Thank you for contributing to the LLM Red Teaming Platform!**

Your contributions help make AI systems more secure and reliable for everyone.
