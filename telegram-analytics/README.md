# Telegram Analytics

A Python package for Telegram channel analytics using the Telethon library.

## Description

This package provides comprehensive analytics functionality for Telegram channels using a userbot approach with Telethon. It includes features for monitoring channel activity, collecting statistics, and analyzing user engagement.

## Features

- Channel statistics collection
- Message analytics
- User engagement tracking
- FastAPI-based REST API
- Async/await support

## Installation

```bash
pip install telegram-analytics
```

Or for development:

```bash
uv sync --dev
```

## Requirements

- Python 3.13+
- Telegram API credentials (api_id and api_hash)
- Active Telegram account

## Quick Start

```python
from telegram_analytics import TelegramAnalytics

# Initialize the analytics client
analytics = TelegramAnalytics(
    api_id=your_api_id,
    api_hash="your_api_hash"
)

# Start collecting analytics
await analytics.start()
```

## Dependencies

- FastAPI (>=0.116.1)
- Pydantic (>=2.11.7)
- Telethon (>=1.40.0)
- Uvicorn (>=0.35.0)

## Development

For development setup:

```bash
# Install development dependencies
uv sync --dev

# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy .
```

## License

See the main project LICENSE file for details.