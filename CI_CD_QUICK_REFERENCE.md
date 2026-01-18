# CI/CD & Testing Setup - Quick Reference

## 🎯 What Was Implemented

Complete GitHub Actions CI/CD pipeline with local pre-commit hooks for automatic testing and code quality checks on every commit.

## 📋 Quick Start

### 1️⃣ First Time Setup (One-Time Only)

```bash
# Install pre-commit framework
pip install pre-commit

# Install git hooks in your repository
pre-commit install

# (Optional) Test all hooks on existing code
pre-commit run --all-files
```

**That's it!** Pre-commit hooks are now active. Code quality checks run automatically before each commit.

### 2️⃣ Normal Development Flow

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes...
# Write tests...

# Stage and commit (pre-commit hooks run automatically)
git add .
git commit -m "Add my feature"

# Pre-commit will:
# ✅ Check code style (Black)
# ✅ Sort imports (isort)
# ✅ Lint code (Flake8)
# ✅ Check types (mypy)
# ✅ Scan security (Bandit)
# ✅ Validate docstrings

# If issues found:
# - Auto-fixable issues are fixed automatically
# - Manual issues require your attention
# - Retry commit after fixes

# Push to GitHub
git push origin feature/my-feature

# GitHub Actions automatically runs:
# ✅ Full test suite
# ✅ Extended linting
# ✅ Code coverage report
# ✅ Security scanning
```

## 🔄 Automated Pipelines

### Backend Pipeline (ctsr-api)
Runs on: Push/PR to main/develop with changes in `ctsr-api/`

```
✅ Tests (Python 3.11, 3.12)
✅ Linting (Flake8)
✅ Formatting (Black)
✅ Import sorting (isort)
✅ Type checking (mypy)
✅ Security scanning (Bandit, Safety)
✅ Coverage reporting (Codecov)
```

### Frontend Pipeline (streamlit-app)
Runs on: Push/PR to main/develop with changes in `streamlit-app/`

```
✅ Tests (Python 3.11, 3.12)
✅ Linting (Flake8, pylint)
✅ Formatting (Black)
✅ Import sorting (isort)
✅ Type checking (mypy)
✅ Code complexity (Radon)
✅ Security scanning (Bandit, Safety)
✅ Coverage reporting (Codecov)
```

### Integration Tests
Runs on: All PRs to main/develop

```
✅ Backend service setup
✅ API health checks
✅ Cross-service communication
✅ End-to-end workflows
```

## 📁 Files Created

### GitHub Actions Workflows
```
.github/workflows/
├── backend-ci.yml           # Backend pipeline
├── frontend-ci.yml          # Frontend pipeline  
├── integration-tests.yml    # Integration tests
└── pre-commit.yml           # Pre-commit on PR
```

### Configuration Files
```
├── .pre-commit-config.yaml           # Local hook config
├── pytest.ini                        # Pytest config
├── ctsr-api/requirements-dev.txt     # Backend dev deps
└── streamlit-app/requirements-dev.txt # Frontend dev deps
```

### Documentation
```
├── TESTING_CI_SETUP.md     # Full CI/CD guide
├── DEVELOPMENT_SETUP.md    # Local dev guide
└── This file (CI_CD_QUICK_REFERENCE.md)
```

## 🛠️ Common Commands

### Install Dev Dependencies
```bash
cd ctsr-api
pip install -r requirements.txt -r requirements-dev.txt

# or for frontend
cd streamlit-app
pip install -r requirements.txt -r requirements-dev.txt
```

### Run Tests Locally
```bash
pytest tests/ -v                    # Run all tests
pytest tests/ --cov=api             # With coverage
pytest tests/test_name.py -v        # Specific test
pytest tests/ -k "vendor" -v        # Pattern matching
```

### Run Code Quality Checks
```bash
black .                              # Format code
isort .                              # Sort imports
flake8 .                             # Lint
mypy . --ignore-missing-imports      # Type check
bandit -r . -ll                      # Security scan
pre-commit run --all-files           # All checks
```

### Format Code Automatically
```bash
# Black (formatter)
black .

# isort (import sorter)  
isort .

# Both
black . && isort .
```

### Fix Linting Issues
```bash
# Auto-fix as much as possible
black . && isort .

# Then manually address remaining issues shown by:
flake8 .
```

## 📊 Checking PR Status

1. **On GitHub**: Go to your PR → "Checks" section
2. **View Results**: Click "Details" next to each check
3. **Fix Issues**: Address any failures locally
4. **Re-push**: `git add . && git commit -m "Fix issues" && git push`

## ⚙️ Manual Linting Commands

### Backend
```bash
cd ctsr-api

# Format
black api/
isort api/

# Check
flake8 api/ --max-line-length=120
mypy api/ --ignore-missing-imports

# Security
bandit -r api/ -ll
```

### Frontend
```bash
cd streamlit-app

# Format
black app/ app.py
isort app/ app.py

# Check
flake8 app/ --max-line-length=120
mypy app/ --ignore-missing-imports

# Security
bandit -r app/ -ll
```

## 🔍 Understanding Failures

### Formatting Issues
→ Run `black . && isort .` to auto-fix

### Type Errors
→ Add type hints or use `# type: ignore` comments

### Import Issues
→ Run `isort .` to auto-fix

### Security Warnings
→ Review Bandit output, fix or suppress

### Test Failures
→ Run locally with `pytest -vv` to debug

## 📚 Detailed Documentation

- **Full CI/CD Guide**: [TESTING_CI_SETUP.md](../TESTING_CI_SETUP.md)
- **Development Workflow**: [DEVELOPMENT_SETUP.md](../DEVELOPMENT_SETUP.md)
- **Pre-commit Config**: [.pre-commit-config.yaml](../.pre-commit-config.yaml)

## ❓ Troubleshooting

### Pre-commit not running
```bash
pre-commit install
pre-commit run --all-files
```

### Pre-commit failing on existing code
```bash
# Fix all files at once
black .
isort .
flake8 --max-line-length=120
```

### Bypass pre-commit (not recommended)
```bash
git commit --no-verify
```

### Uninstall pre-commit
```bash
pre-commit uninstall
```

## ✅ Before Merging PR

Make sure all of these pass:
- ✅ Backend CI pipeline
- ✅ Frontend CI pipeline
- ✅ Integration tests
- ✅ Code coverage maintained
- ✅ No security issues
- ✅ Approved by reviewer

## 🎯 Best Practices

1. **Always install pre-commit** on first clone
2. **Run tests locally** before pushing
3. **Fix linting early** - don't let it accumulate
4. **Review CI logs** for any failures
5. **Keep commits clean** - run formatting before commit

## 🚀 Workflow Summary

```
Local Development
    ↓
Make changes
    ↓
Run: git commit
    ↓
Pre-commit hooks run ✅
    (If issues, fix and retry)
    ↓
Push to GitHub
    ↓
GitHub Actions pipelines run ✅
    (Backend, Frontend, Integration)
    ↓
Code review
    ↓
Merge after approval ✅
```

## 📞 Support

For issues:
1. Check [TESTING_CI_SETUP.md](../TESTING_CI_SETUP.md) for details
2. Review CI logs on GitHub Actions
3. Run checks locally to reproduce
4. Check [DEVELOPMENT_SETUP.md](../DEVELOPMENT_SETUP.md) for examples

---

**Status**: ✅ All CI/CD pipelines active and ready!
