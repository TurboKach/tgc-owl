# 🧪 Testing Guide - Telegram Analytics Bot

This guide explains the comprehensive testing system for the Telegram Analytics Bot, making it easy to run different types of tests and validate functionality.

## 🚀 Quick Start Commands

### For New Users
```bash
# Full setup and validation
make setup          # Install deps + create .env
make validate       # Validate configuration
make auth           # Test authentication
make test-conn      # Test connectivity
```

### For Developers
```bash
# Development workflow
make test           # Run all internal tests
make test-cov       # Run tests with coverage
make format         # Format code
make lint           # Check code quality
```

## 📋 Test Categories

### 1. 🔧 **Internal Tests** (`make test`)
**Purpose:** Code quality and unit testing  
**Runtime:** ~30 seconds  
**Includes:**
- ✅ Unit tests (pytest)
- ✅ Linting (ruff)
- ✅ Type checking (mypy)
- ✅ Code formatting validation (black)

```bash
# Run all internal tests
make test

# Individual components
make test-unit      # Unit tests only
make lint           # Linting only
make type           # Type checking only
```

### 2. 🌐 **Connectivity Tests** (`make test-conn`)
**Purpose:** Test external connections and integrations  
**Runtime:** ~10 seconds  
**Includes:**
- ✅ Module imports
- ✅ Configuration loading
- ✅ Session file handling
- ✅ Telegram API connection
- ✅ User authentication status

```bash
# Run connectivity tests
make test-conn

# Alternative
uv run python test_connectivity.py
```

### 3. 🔐 **Authentication Tests** (`make auth`)
**Purpose:** Test Telegram authentication flow  
**Runtime:** ~5 seconds  
**Includes:**
- ✅ API credential validation
- ✅ Session persistence
- ✅ Code request flow
- ✅ User information retrieval

```bash
# Test authentication (sends code)
make auth

# Complete authentication with verification code
make auth-setup
```

### 4. ✅ **Setup Validation** (`make validate`)
**Purpose:** Verify installation and configuration  
**Runtime:** ~3 seconds  
**Includes:**
- ✅ All modules importable
- ✅ Configuration loads correctly
- ✅ Dependencies installed
- ✅ Project structure valid

```bash
# Validate complete setup
make validate
```

## 📊 Test Coverage

Current test coverage (as of Step 1.1):

```
Name                                      Stmts   Miss  Cover   Missing
-----------------------------------------------------------------------
src/telegram_analytics/core/config.py       61      9    85%   
src/telegram_analytics/core/client.py      126     47    63%   
-----------------------------------------------------------------------
TOTAL                                       189     57    70%
```

**Target:** 80%+ coverage for Step 1.2

## 🛠️ Development Workflow

### Pre-Commit Checks
```bash
make format         # Auto-format code
make lint           # Check linting
make type           # Check types
make test-unit      # Run unit tests
```

### Full Validation
```bash
make test           # All internal tests
make test-conn      # Connectivity tests
make validate       # Setup validation
```

### Adding New Features
1. **Write tests first** (TDD approach)
2. **Run `make test-unit`** to ensure new tests fail
3. **Implement feature**
4. **Run `make test`** to ensure all tests pass
5. **Run `make test-conn`** to verify integration

## 🎯 Test Results Interpretation

### ✅ Success Indicators
- All tests show `✅ PASSED`
- Coverage above 70%
- No linting errors
- Type checking passes

### ⚠️ Warning Signs
- Connectivity tests fail (check .env config)
- Authentication tests fail (check API credentials)
- Coverage drops below 60%

### ❌ Failure Actions
1. **Unit test failures:** Fix code logic
2. **Linting failures:** Run `make format`
3. **Type failures:** Add missing type hints
4. **Connectivity failures:** Check configuration

## 📁 Test File Structure

```
telegram-analytics/
├── run_tests.py           # Main test runner
├── test_connectivity.py   # Connectivity tests
├── test_login.py          # Authentication tests
├── validate_setup.py      # Setup validation
├── Makefile              # Easy commands
├── tests/
│   ├── test_client.py    # Unit tests for client
│   └── __init__.py
└── src/telegram_analytics/
    └── core/
        ├── client.py     # Main client code
        └── config.py     # Configuration
```

## 🚦 CI/CD Integration

For automated testing, use:

```bash
# Full validation pipeline
make setup && make test && make test-conn && make validate
```

This ensures:
1. ✅ Dependencies installed
2. ✅ Code quality validated
3. ✅ External connections work
4. ✅ Setup is complete

## 💡 Pro Tips

### Speed Up Testing
```bash
make test-unit          # Skip slow connectivity tests
pytest tests/test_client.py::TestName  # Run specific test
```

### Debug Test Failures
```bash
make test-unit-v        # Verbose output
pytest tests/ -x        # Stop on first failure
pytest tests/ --pdb     # Debug on failure
```

### Coverage Analysis
```bash
make test-cov           # Show coverage report
pytest --cov-html=htmlcov tests/  # HTML coverage report
```

---

**Testing System Status:** ✅ **Complete and Production Ready**

The testing system provides comprehensive validation for all aspects of the Telegram Analytics Bot, from code quality to external integrations, making development and deployment reliable and efficient.