# GitHub Actions & Testing Setup Guide

## Overview

This project includes comprehensive CI/CD pipelines via GitHub Actions to ensure code quality, security, and test coverage on every commit and pull request.

## GitHub Actions Workflows

### 1. Backend CI Pipeline (`backend-ci.yml`)
**Triggers**: Push/PR to main/develop with changes to `ctsr-api/`

**Steps**:
- ✅ Python 3.11 & 3.12 compatibility testing
- ✅ Flake8 linting
- ✅ Black code formatting check
- ✅ isort import ordering check
- ✅ mypy type checking
- ✅ pytest test suite
- ✅ Code coverage reporting (Codecov)
- ✅ Security scanning (Bandit, Safety)

**Coverage**: API code and models

### 2. Frontend CI Pipeline (`frontend-ci.yml`)
**Triggers**: Push/PR to main/develop with changes to `streamlit-app/`

**Steps**:
- ✅ Python 3.11 & 3.12 compatibility testing
- ✅ Flake8 linting
- ✅ Black code formatting check
- ✅ isort import ordering check
- ✅ mypy type checking
- ✅ pylint linting
- ✅ pytest test suite
- ✅ Code complexity analysis (Radon)
- ✅ Security scanning (Bandit, Safety)

**Coverage**: App code and utilities

### 3. Integration Tests (`integration-tests.yml`)
**Triggers**: Push/PR to main/develop

**Steps**:
- ✅ Sets up API service
- ✅ Tests API endpoint connectivity
- ✅ Runs integration tests
- ✅ Validates end-to-end workflows

### 4. Pre-commit Hooks (`pre-commit.yml`)
**Triggers**: Pull requests

**Steps**:
- ✅ Runs pre-commit checks on changed files
- ✅ Comments on PR with results
- ✅ Helps catch issues before merge

## Local Development Setup

### Install Pre-commit Hooks

Pre-commit hooks run code quality checks before you commit:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hook scripts
pre-commit install

# (Optional) Run against all files
pre-commit run --all-files
```

### Pre-commit Configuration

The `.pre-commit-config.yaml` file includes:

1. **File Checks**
   - Trailing whitespace removal
   - End-of-file fixer
   - YAML/JSON validation
   - Merge conflict detection
   - Large file detection

2. **Python Code Quality**
   - Black (code formatting)
   - isort (import sorting)
   - Flake8 (linting)
   - mypy (type checking)
   - Bandit (security)
   - Interrogate (docstring coverage)

3. **Excluded Directories**
   - Virtual environments
   - Build artifacts
   - Cache directories
   - Migrations

## Running Tests Locally

### Backend Tests
```bash
cd ctsr-api

# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run specific test file
pytest tests/test_vendors.py -v

# Run specific test
pytest tests/test_vendors.py::test_create_vendor -v
```

### Frontend Tests
```bash
cd streamlit-app

# Install test dependencies
pip install pytest pytest-cov

# Run all tests (if they exist)
pytest tests/ -v 2>/dev/null || echo "No tests found"

# Run specific test
pytest tests/test_api_client.py -v
```

## Running Linting Locally

### Backend
```bash
cd ctsr-api

# Flake8
flake8 api/ --max-line-length=120

# Black
black api/ --line-length=120

# isort
isort api/

# mypy
mypy api/ --ignore-missing-imports

# Bandit
bandit -r api/ -ll

# All at once
black api/ && isort api/ && flake8 api/ && mypy api/
```

### Frontend
```bash
cd streamlit-app

# Flake8
flake8 app/ --max-line-length=120

# Black
black app/ app.py --line-length=120

# isort
isort app/ app.py

# mypy
mypy app/ --ignore-missing-imports

# All at once
black app/ app.py && isort app/ app.py && flake8 app/
```

## Checking Coverage Reports

After running tests with coverage:

```bash
# Backend coverage
cd ctsr-api
pip install coverage
coverage report
coverage html
# Open htmlcov/index.html in browser

# Frontend coverage
cd streamlit-app
coverage report
coverage html
# Open htmlcov/index.html in browser
```

## CI/CD Dashboard

View workflow status at: `https://github.com/YOUR_USERNAME/Clinical_Trial_System_Solution/actions`

### Checking PR Status
1. Open a Pull Request
2. Scroll to "Checks" section
3. View workflow status for each pipeline
4. Click "Details" to see full logs

## Understanding CI Failures

### Failed Linting
If Black/isort/Flake8 fails:
```bash
# Auto-fix formatting issues
black .
isort .

# Then commit the changes
git add -A
git commit -m "Fix code formatting"
```

### Failed Type Checking
If mypy fails:
```bash
# View errors
mypy app/ --ignore-missing-imports

# Add type hints or ignore specific errors
# :type: ignore  # noqa
```

### Failed Tests
If pytest fails:
1. Run test locally to reproduce
2. Check test output for details
3. Fix the code
4. Re-run test to verify

### Security Issues
If Bandit/Safety fails:
- Review security warnings
- Update vulnerable dependencies
- Or suppress false positives with comments

## Test Coverage Goals

| Component | Target Coverage |
|-----------|-----------------|
| Backend API | 80%+ |
| Frontend App | 60%+ |
| Utils | 85%+ |
| Models | 90%+ |

## Adding New Tests

### Backend
Create `ctsr-api/tests/test_yourmodule.py`:
```python
import pytest
from api.yourmodule import some_function

def test_some_function():
    result = some_function("input")
    assert result == "expected"
```

### Frontend
Create `streamlit-app/tests/test_yourmodule.py`:
```python
import pytest
from app.utils.yourmodule import some_function

def test_some_function():
    result = some_function("input")
    assert result == "expected"
```

## CI/CD Configuration Files

- `.github/workflows/backend-ci.yml` - Backend pipeline
- `.github/workflows/frontend-ci.yml` - Frontend pipeline
- `.github/workflows/integration-tests.yml` - Integration tests
- `.github/workflows/pre-commit.yml` - Pre-commit hooks
- `.pre-commit-config.yaml` - Local pre-commit configuration

## Troubleshooting

### Pre-commit not running
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install
```

### CI failing but local tests pass
- Ensure you're using same Python version (3.11/3.12)
- Check for platform-specific issues (Windows vs Linux)
- Review CI logs for exact error

### Coverage not uploading
- Check Codecov token is set in GitHub secrets
- Verify coverage.xml file is generated
- Check repository permissions

## Best Practices

1. **Always run pre-commit before pushing**
   ```bash
   pre-commit run --all-files
   ```

2. **Run tests before creating PR**
   ```bash
   pytest tests/ -v
   ```

3. **Check type hints**
   ```bash
   mypy . --ignore-missing-imports
   ```

4. **Keep code coverage above target**
   - Write tests for new features
   - Maintain existing test coverage

5. **Fix style issues immediately**
   - Don't let them accumulate
   - Use auto-formatters (Black, isort)

## GitHub Status Checks

All PRs require:
- ✅ Backend CI to pass
- ✅ Frontend CI to pass
- ✅ Code review approval

Before merging to main, ensure:
- All checks pass ✅
- Coverage maintained
- No security issues
- Code quality acceptable

## Advanced Usage

### Skip CI for specific commits
```bash
git commit --no-verify  # Skips pre-commit (not recommended)
```

### Run specific workflow
```bash
gh workflow run backend-ci.yml --ref main
```

### View workflow logs
```bash
gh run view <run-id> --log
```

## Support

For CI/CD issues:
1. Check workflow logs on GitHub Actions
2. Run same checks locally to reproduce
3. Review `.pre-commit-config.yaml` for tool versions
4. Check GitHub Actions documentation

## References

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)
- [isort Documentation](https://pycqa.github.io/isort/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [mypy Type Checker](https://mypy.readthedocs.io/)
- [Bandit Security Linter](https://bandit.readthedocs.io/)
