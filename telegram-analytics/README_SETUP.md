# Telegram Analytics - Setup Guide

## Quick Start

This guide will help you set up and test the Telegram Analytics userbot client.

### Prerequisites

1. **Python 3.13+** (using UV package manager)
2. **Telegram API credentials** from [my.telegram.org](https://my.telegram.org)
3. **Phone number** with access to Telegram

### Step 1: Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Go to "API development tools"
4. Create a new application
5. Note down your `api_id` and `api_hash`

### Step 2: Configure Environment

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   # Required: Your Telegram API credentials
   TELEGRAM_API_ID=123456789
   TELEGRAM_API_HASH=your_api_hash_here
   TELEGRAM_PHONE_NUMBER=+1234567890
   
   # Optional: Other settings
   SECRET_KEY=your_random_secret_key_here
   DATABASE_PASSWORD=your_db_password
   ```

### Step 3: Install Dependencies

```bash
cd telegram-analytics
uv sync
```

### Step 4: Test Telegram Authentication

#### Option A: Interactive Test
```bash
uv run python test_login.py
```

This will:
- Load your configuration
- Initialize the Telegram client
- Check if you're already authenticated
- If not, send a verification code to your phone

#### Option B: Complete Authentication
If you received a verification code, complete the auth:
```bash
uv run python test_login.py --complete
```

This will prompt you for:
- Phone number (uses config if empty)
- Verification code from SMS/Telegram
- 2FA password (if enabled)

### Step 5: Verify Success

If authentication succeeds, you should see:
```
✅ Authentication test completed successfully!
Logged in as: Your Name (@yourusername)
Phone: +1234567890
User ID: 123456789
```

### Session Storage

- Session files are stored in `sessions/` directory
- The session file (`telegram_analytics.session`) contains your authentication tokens
- **NEVER commit session files to git** - they're already in `.gitignore`

### Troubleshooting

#### Invalid API credentials
```
telegram.errors.rpcerrorlist.ApiIdInvalidError: The api_id/api_hash combination is invalid
```
**Solution:** Double-check your `api_id` and `api_hash` from my.telegram.org

#### Phone number issues
```
telegram.errors.rpcerrorlist.PhoneNumberInvalidError: The phone number is invalid
```
**Solution:** Ensure phone number includes country code (e.g., `+1234567890`)

#### Rate limiting
```
telegram.errors.rpcerrorlist.FloodWaitError: A wait of X seconds is required
```
**Solution:** Wait the specified time before trying again

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/telegram_analytics

# Run specific test file
uv run pytest tests/test_client.py -v
```

### Next Steps

Once authentication works:
1. ✅ **Step 1.1 Complete** - Telethon Login & Session
2. 🚧 **Step 1.2** - Channel Joining & Admin Verification  
3. ⏭️ **Step 1.3** - User Event Tracking

### Security Notes

- Keep your `.env` file secure and never commit it
- Session files contain authentication tokens - treat them like passwords
- API keys have rate limits - don't abuse them
- Test with a dedicated test channel first

### File Structure

```
telegram-analytics/
├── src/telegram_analytics/core/
│   ├── config.py          # Configuration management
│   └── client.py          # Telethon client wrapper
├── tests/
│   └── test_client.py     # Unit tests
├── test_login.py          # Authentication test script
├── .env.example           # Environment template
└── .env                   # Your config (create this)
```