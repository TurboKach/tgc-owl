# Telegram Analytics Setup Guide

This guide provides detailed setup instructions for the Telegram Analytics package.

## Prerequisites

Before setting up the Telegram Analytics package, ensure you have:

- **Python 3.13+** installed
- **UV package manager** (recommended) or pip
- **Git** for version control
- **Telegram account** with phone number access
- **Telegram API credentials** (see below)

## Step 1: Environment Setup

### Install UV (Recommended)

```bash
# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verify installation
uv --version
```

### Alternative: Using pip

If you prefer using pip instead of UV:

```bash
# Ensure you have Python 3.13+
python --version

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Step 2: Get Telegram API Credentials

1. **Visit Telegram API Portal**
   - Go to [my.telegram.org](https://my.telegram.org)
   - Log in with your phone number

2. **Create Application**
   - Navigate to ["API development tools"](https://my.telegram.org/apps)
   - Click "Create new application"
   - Fill in the form:
     - **App title**: `Telegram Analytics Bot`
     - **Short name**: `tg-analytics`
     - **Platform**: Choose appropriate platform
     - **Description**: `Analytics bot for Telegram channels`

3. **Save Credentials**
   - Copy your `api_id` (numeric value)
   - Copy your `api_hash` (string value)
   - **Keep these secure and private!**

## Step 3: Project Setup

### Clone and Install

```bash
# Navigate to the telegram-analytics directory
cd telegram-analytics

# Install dependencies with UV
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Environment Configuration

1. **Create environment file**
   ```bash
   cp .env.example .env
   ```

2. **Edit environment variables**
   ```bash
   # Edit .env file with your credentials
   nano .env  # or use your preferred editor
   ```

3. **Set required variables**
   ```env
   # Telegram API credentials
   TELEGRAM_API_ID=your_api_id_here
   TELEGRAM_API_HASH=your_api_hash_here
   
   # Optional: Phone number (for automated login)
   TELEGRAM_PHONE=+1234567890
   
   # Database configuration (optional)
   DATABASE_URL=sqlite:///telegram_analytics.db
   
   # Logging level
   LOG_LEVEL=INFO
   ```

## Step 4: Verification

### Test Setup

```bash
# Run setup validation
python validate_setup.py

# Run basic tests
pytest tests/

# Check connectivity
python test_connectivity.py
```

### First Login

```bash
# Test Telegram login
python test_login.py
```

You'll be prompted to:
1. Enter your phone number
2. Enter the verification code sent via Telegram
3. Enter 2FA password if enabled

## Step 5: Development Setup

### Code Quality Tools

```bash
# Install pre-commit hooks
pre-commit install

# Run linting
ruff check .

# Run type checking
mypy .

# Format code
black .
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=telegram_analytics

# Run specific test
pytest tests/test_client.py -v
```

## Troubleshooting

### Common Issues

1. **API Credentials Invalid**
   - Verify api_id and api_hash are correct
   - Check that your Telegram account is active
   - Ensure no extra spaces in environment variables

2. **Phone Number Issues**
   - Use international format: +1234567890
   - Ensure the number is associated with your Telegram account
   - Try logging in manually first

3. **Permission Errors**
   - Check that your account has access to target channels
   - Verify bot permissions if using bot token
   - Some channels may require manual joining first

4. **Dependencies Issues**
   - Ensure Python 3.13+ is installed
   - Clear UV cache: `uv cache clean`
   - Try recreating virtual environment

### Getting Help

- Check the main README.md for general information
- Review test files for usage examples
- Check GitHub issues for known problems
- Ensure all prerequisites are met

## Security Notes

- **Never commit your .env file**
- **Keep API credentials secure**
- **Use environment variables in production**
- **Regularly rotate API credentials**
- **Limit API access to necessary scopes**

## Next Steps

After successful setup:

1. Review the main package documentation
2. Explore example scripts in the `examples/` directory
3. Run the test suite to verify functionality
4. Start developing your analytics workflows

For more information, see the main project README.md file.