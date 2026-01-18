# Development Setup & Local Development Guide

## Quick Setup

### 1. Clone Repository
```bash
git clone https://github.com/YOUR_USERNAME/Clinical_Trial_System_Solution.git
cd Clinical_Trial_System_Solution
```

### 2. Setup Pre-commit Hooks
```bash
pip install pre-commit
pre-commit install
```

Now code quality checks run automatically before each commit!

### 3. Backend Development

#### Setup
```bash
cd ctsr-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Run Tests
```bash
pytest tests/ -v --cov=api --cov-report=html
```

#### Run Linting
```bash
# Format code
black api/ --line-length=120
isort api/

# Check for issues
flake8 api/ --max-line-length=120
mypy api/ --ignore-missing-imports

# Security check
bandit -r api/ -ll
```

#### Start Server
```bash
python main.py
# API at http://localhost:8001
```

### 4. Frontend Development

#### Setup
```bash
cd streamlit-app
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### Run Tests
```bash
pytest tests/ -v --cov=app --cov-report=html
```

#### Run Linting
```bash
# Format code
black app/ app.py --line-length=120
isort app/ app.py

# Check for issues
flake8 app/ --max-line-length=120
mypy app/ --ignore-missing-imports

# Security check
bandit -r app/ -ll
```

#### Start App
```bash
streamlit run app.py
# App at http://localhost:8501
```

## Development Workflow

### Before Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Install pre-commit hooks** (first time only)
   ```bash
   pre-commit install
   ```

### Making Changes

1. **Write code**
   ```bash
   # Edit files...
   ```

2. **Write tests**
   ```bash
   # Add tests to tests/ directory
   ```

3. **Run tests locally**
   ```bash
   pytest tests/ -v
   ```

4. **Run code quality checks**
   ```bash
   # Will run automatically on commit if pre-commit installed
   # Or manually:
   pre-commit run --all-files
   ```

5. **Commit changes**
   ```bash
   git add .
   git commit -m "Add my feature"
   # Pre-commit hooks run automatically
   ```

### Pushing & Pull Request

1. **Push branch**
   ```bash
   git push origin feature/my-feature
   ```

2. **Create PR on GitHub**
   - Describe changes
   - Reference related issues
   - Wait for CI/CD to complete

3. **Address review comments**
   ```bash
   # Make changes
   git add .
   git commit -m "Address review feedback"
   git push
   ```

4. **Merge after approval**
   - All checks must pass ✅
   - At least 1 approval required
   - Then click "Merge"

## Code Quality Standards

### Python Style
- **Formatter**: Black (line length 120)
- **Import Sorter**: isort
- **Linter**: Flake8 (max complexity 10)

### Type Hints
- Use mypy for type checking
- Add type hints to functions
- Document complex types

### Testing
- Minimum coverage: 60%
- All public functions tested
- Include edge cases

### Security
- Bandit scans for issues
- Safety checks for vulnerabilities
- No hardcoded secrets

### Documentation
- Docstrings for all functions
- README for setup
- Comments for complex logic

## Running All Checks Locally

### Quick Check
```bash
# Format and lint everything
black . && isort . && flake8 . && mypy . --ignore-missing-imports
```

### Full Check (Backend)
```bash
cd ctsr-api
black api/ && \
isort api/ && \
flake8 api/ && \
mypy api/ --ignore-missing-imports && \
pytest tests/ -v && \
bandit -r api/ -ll
```

### Full Check (Frontend)
```bash
cd streamlit-app
black app/ app.py && \
isort app/ app.py && \
flake8 app/ && \
mypy app/ --ignore-missing-imports && \
pytest tests/ -v && \
bandit -r app/ -ll
```

## Common Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_vendors.py::test_create_vendor -v

# Run with coverage
pytest tests/ --cov=api --cov-report=html

# Run only failed tests
pytest tests/ --lf

# Run tests matching pattern
pytest tests/ -k "vendor" -v
```

### Code Formatting
```bash
# Format all Python files
black .

# Check without formatting
black --check .

# Sort imports
isort .

# Check import order
isort --check-only .
```

### Linting
```bash
# Run flake8
flake8 . --max-line-length=120

# Run mypy
mypy . --ignore-missing-imports

# Run pylint
pylint app/
```

### Pre-commit
```bash
# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files

# Uninstall hooks
pre-commit uninstall
```

## Debugging

### Debug with print statements
```python
# In code
print(f"Debug: {variable}")

# Then run:
pytest tests/test_name.py -v -s  # -s shows output
```

### Debug with pdb
```python
# In code
import pdb; pdb.set_trace()

# Run test - it will pause at breakpoint
pytest tests/test_name.py -v -s
```

### Debug with IDE
- VS Code: Install Python extension, set breakpoints, hit F5
- PyCharm: Set breakpoints, run tests in debug mode

## Troubleshooting

### Pre-commit not running
```bash
# Check if installed
pre-commit --version

# Reinstall
pre-commit uninstall
pre-commit install
```

### Black formatting conflicts
```bash
# Run black to auto-fix
black .

# Then commit
git add -A
git commit -m "Fix formatting"
```

### Tests failing locally but passing on CI
- Check Python version: `python --version` (should be 3.11+)
- Check dependencies: `pip install -r requirements.txt -r requirements-dev.txt`
- Check for platform-specific issues

### Imports not resolving in IDE
```bash
# Make sure venv is activated
source venv/bin/activate

# Reinstall packages
pip install -r requirements.txt

# In VS Code: Ctrl+Shift+P → Python: Select Interpreter → Choose venv
```

## Best Practices

### Commit Messages
```
[Good] Add user authentication to vendors API
[Good] Fix bug in system validation
[Good] Refactor database queries for performance

[Bad] update
[Bad] fixed stuff
[Bad] changes
```

### Code Comments
```python
# [Good] Explain why, not what
# We retry 3 times because the API can be temporarily unavailable
retry_count = 3

# [Bad] Just restates the code
# Set retry count to 3
retry_count = 3
```

### Pull Request Descriptions
```markdown
## Changes
- Added new API endpoint for bulk vendor import
- Improved error handling in system validation

## Testing
- Added 5 new tests in test_vendors.py
- All tests pass locally

## Related Issues
Fixes #123
Related to #456
```

## Performance Tips

### Pytest Performance
```bash
# Run only changed tests
pytest tests/ --lf

# Run in parallel
pip install pytest-xdist
pytest tests/ -n auto

# Stop on first failure
pytest tests/ -x
```

### Code Coverage
```bash
# Find untested code
coverage report

# Generate HTML report
coverage html
open htmlcov/index.html
```

## Tools & Extensions

### VS Code Extensions
- Python (Microsoft)
- Pylance
- Black Formatter
- isort
- Flake8
- Thunder Client (API testing)

### PyCharm
- Built-in code inspections
- Integrated pytest
- Code coverage
- Git integration

### Git Hooks
`.pre-commit-config.yaml` includes:
- Black formatting
- isort import sorting
- Flake8 linting
- mypy type checking
- Bandit security
- Interrogate docstrings

## CI/CD Integration

### GitHub Actions
- Automatic testing on push
- Automatic linting on PR
- Coverage reports
- Security scanning

See [TESTING_CI_SETUP.md](TESTING_CI_SETUP.md) for details.

## Resources

- [Git Documentation](https://git-scm.com/doc)
- [Pytest Guide](https://docs.pytest.org/)
- [Black Code Style](https://black.readthedocs.io/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)

## Questions?

1. Check existing documentation
2. Review code examples
3. Check similar implementations
4. Ask team members
5. Create GitHub issue

Happy coding! 🚀
