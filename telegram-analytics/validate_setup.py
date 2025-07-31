#!/usr/bin/env python3
"""Validate that Step 1.1 setup is working correctly."""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_imports():
    """Test that all core modules can be imported."""
    try:
        from src.telegram_analytics.core import config, client

        print("✅ All core modules import successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_config():
    """Test configuration system."""
    try:
        from src.telegram_analytics.core.config import get_config

        config = get_config()
        print("✅ Configuration loaded")
        print(f"   - Session path: {config.telegram.session_path}")
        print(f"   - API ID: {config.telegram.api_id} (set to 0 = needs configuration)")
        print(f"   - Database URL: {config.database.url}")

        # Check if actual credentials are provided
        if config.telegram.api_id == 0 or not config.telegram.api_hash:
            print("⚠️  Warning: Telegram API credentials not configured")
            print("   Please copy .env.example to .env and add your credentials")
            return False
        else:
            print("✅ Telegram API credentials configured")
            return True

    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


async def test_client_creation():
    """Test client creation (without connecting)."""
    try:
        from src.telegram_analytics.core.client import TelegramAnalyticsClient
        from src.telegram_analytics.core.config import TelegramConfig

        # Create test config
        test_config = TelegramConfig(
            api_id=123456, api_hash="test_hash", session_name="test_session"
        )

        client = TelegramAnalyticsClient(test_config)
        await client.initialize()

        print("✅ Client creation works")
        return True

    except Exception as e:
        print(f"❌ Client creation error: {e}")
        return False


def main():
    """Run all validation tests."""
    print("🔍 Validating Step 1.1 setup...\n")

    # Test imports
    if not test_imports():
        sys.exit(1)

    # Test configuration
    config_ok = test_config()

    # Test client creation
    import asyncio

    try:
        client_ok = asyncio.run(test_client_creation())
    except Exception as e:
        print(f"❌ Async client test failed: {e}")
        client_ok = False

    print("\n📋 Summary:")
    print("   Core imports: ✅")
    print(f"   Configuration: {'✅' if config_ok else '⚠️'}")
    print(f"   Client creation: {'✅' if client_ok else '❌'}")

    if config_ok and client_ok:
        print("\n🎉 Step 1.1 validation passed!")
        print("\n📝 Next steps:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your Telegram API credentials")
        print("   3. Run: uv run python test_login.py")
        return True
    else:
        print("\n❌ Step 1.1 validation failed!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
