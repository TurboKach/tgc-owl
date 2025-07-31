# Telegram Channel Analytics Bot (TGC-Owl)

[![CI Pipeline](https://github.com/turbokach/tgc-owl/actions/workflows/ci.yml/badge.svg)](https://github.com/turbokach/tgc-owl/actions/workflows/ci.yml)
[![Nightly Tests](https://github.com/turbokach/tgc-owl/actions/workflows/nightly.yml/badge.svg)](https://github.com/turbokach/tgc-owl/actions/workflows/nightly.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: ruff](https://img.shields.io/badge/linting-ruff-red.svg)](https://github.com/astral-sh/ruff)
[![Type checking: mypy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://github.com/python/mypy)

An assistant for maintaining Telegram channels, providing comprehensive analytics functionality using Telethon userbot approach.

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+**
- **UV package manager** (recommended) or pip
- **Telegram API credentials** from [my.telegram.org](https://my.telegram.org)
- **Phone number** with access to Telegram

### 1. Clone and Setup

```bash
git clone <your-repo>
cd tgc-owl/telegram-analytics

# Install dependencies
uv sync
# or with pip: pip install -e .
```

### 2. Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Navigate to ["API development tools"](https://my.telegram.org/apps)
4. Create a new application:
   - **App title**: `Telegram Analytics Bot`
   - **Short name**: `tg-analytics` (or any short name)
   - **Platform**: Choose appropriate platform
5. **Save your `api_id` and `api_hash`** - you'll need these!

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Add your Telegram API credentials to `.env`:
```env
# Required: Your Telegram API credentials
TELEGRAM_API_ID=123456789
TELEGRAM_API_HASH=your_api_hash_here
TELEGRAM_PHONE_NUMBER=+1234567890

# Optional: Other settings
SECRET_KEY=your_random_secret_key_here
DATABASE_PASSWORD=your_db_password
```

### 4. Test Authentication

#### Quick Commands (Recommended)
```bash
# Validate setup
make validate

# Test authentication
make auth

# Complete authentication with code
make auth-setup
```

#### Alternative Commands
```bash
# Using Python scripts directly
uv run python validate_setup.py     # Validate setup
uv run python test_login.py         # Start authentication
uv run python test_login.py --complete # Complete with code
```

#### Expected Success Output
```
✅ Authentication test completed successfully!
Logged in as: Your Name (@yourusername)
Phone: +1234567890
User ID: 123456789
```

### 5. Run Tests

#### Quick Commands (Recommended)
```bash
# Run all internal tests (unit + linting + type checking)
make test

# Run only unit tests
make test-unit

# Run unit tests with coverage
make test-cov

# Run connectivity tests (tests actual Telegram connection)
make test-conn
```

#### Alternative Commands
```bash
# Using Python scripts directly
uv run python run_tests.py           # All internal tests
uv run python run_tests.py --unit    # Unit tests only
uv run python run_tests.py --coverage # Unit tests with coverage
uv run python test_connectivity.py   # Connectivity tests

# Using pytest directly
uv run pytest tests/ -v              # Unit tests verbose
uv run pytest tests/test_client.py   # Specific test file
```

## 📋 Current Status

### ✅ What's Working (Step 1.1 Complete)

- **Authentication System**: Full Telethon userbot authentication
- **Session Management**: Persistent session storage and reuse
- **Configuration**: Environment-based configuration with Pydantic
- **Error Handling**: Proper handling of Telegram API errors
- **Testing**: Unit tests and validation scripts

### 🚧 In Development (Step 1.2)

- Channel joining via invite links
- Admin rights verification
- Channel management functionality

### 📁 Project Structure

```
telegram-analytics/
├── src/telegram_analytics/
│   └── core/
│       ├── config.py          # Configuration management
│       └── client.py          # Telethon client wrapper
├── tests/
│   └── test_client.py         # Unit tests
├── .env.example              # Environment template
├── .env                      # Your config (create this)
├── test_login.py             # Authentication test
├── validate_setup.py         # Setup validation
└── sessions/                 # Session storage (auto-created)
```

## 🔧 Development

### Easy Commands
```bash
# See all available commands
make help

# Install dependencies
make install

# Setup project (install + create .env)
make setup

# Code quality
make format        # Format code with black + ruff
make lint          # Run linting checks
make type          # Run type checking

# Testing
make test          # Run all internal tests
make test-unit     # Run unit tests only
make test-cov      # Run tests with coverage
make test-conn     # Run connectivity tests

# Cleanup
make clean         # Clean cache and temp files
```

### Manual Commands
```bash
# Adding Dependencies
uv add package-name        # Production dependency
uv add --dev package-name  # Development dependency

# Code Quality (manual)
uv run black src/ tests/             # Format code
uv run ruff check src/ tests/        # Lint code
uv run mypy src/telegram_analytics/  # Type checking
```

## 🛡️ Security Notes

- **Never commit** `.env` files or session files to git
- Session files contain authentication tokens - treat them like passwords
- API credentials have rate limits - don't abuse them
- Test with a dedicated test channel first

## 🛠 Development

### Contributing
We use a comprehensive CI/CD pipeline to ensure code quality:

- **Automated Testing**: Unit tests, linting, type checking, and security scans
- **Multiple Python Versions**: Testing on Python 3.11, 3.12, and 3.13
- **Code Quality**: Black formatting, Ruff linting, MyPy type checking
- **Pull Request Validation**: Automated checks for all contributions

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes with proper tests
4. Run local tests: `make test`
5. Submit a pull request
6. CI automatically validates your changes

### Code Quality Standards
- ✅ 100% of tests must pass
- ✅ Code coverage minimum: 50%
- ✅ All linting checks must pass
- ✅ Type hints required for all functions
- ✅ Black code formatting enforced
- ✅ Security scans must pass

## 📖 Documentation

- **Setup Guide**: `telegram-analytics/README_SETUP.md`
- **Testing Guide**: `telegram-analytics/TESTING_GUIDE.md`
- **CI/CD Guide**: `.github/CI_GUIDE.md`
- **Development Plan**: `DEVELOPMENT_PLAN.md`

## 🔗 Useful Links

- [Telethon Documentation](https://docs.telethon.dev/)
- [Telegram API Documentation](https://core.telegram.org/api)
- [Get API Credentials](https://my.telegram.org)

## 🐛 Troubleshooting

### Common Issues

**Invalid API credentials:**
```
telegram.errors.rpcerrorlist.ApiIdInvalidError: The api_id/api_hash combination is invalid
```
→ Double-check your `api_id` and `api_hash` from my.telegram.org

**Phone number issues:**
```
telegram.errors.rpcerrorlist.PhoneNumberInvalidError: The phone number is invalid  
```
→ Ensure phone number includes country code (e.g., `+1234567890`)

**Rate limiting:**
```
telegram.errors.rpcerrorlist.FloodWaitError: A wait of X seconds is required
```
→ Wait the specified time before trying again

### Getting Help

1. Check the setup guide: `telegram-analytics/README_SETUP.md`
2. Run validation: `uv run python validate_setup.py`
3. Check logs in the console output
4. Review unit tests for examples: `tests/test_client.py`

## 🎯 Next Steps

Once authentication is working:

1. **Test with your credentials** using the setup guide
2. **Join a test channel** to verify userbot functionality  
3. **Implement Step 1.2** - Channel joining and admin verification
4. **Continue with the development plan** for full analytics features

---

**Current Phase**: Step 1.1 ✅ Complete | Step 1.2 🚧 In Progress
