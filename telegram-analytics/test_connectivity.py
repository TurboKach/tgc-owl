#!/usr/bin/env python3
"""
Connectivity and integration tests for Telegram Analytics Bot.
Tests actual connections to external services (Telegram API, etc.).
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.telegram_analytics.core.config import get_config
from src.telegram_analytics.core.client import TelegramAnalyticsClient

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_config_loading():
    """Test configuration loading."""
    print("\n🔧 Testing Configuration Loading")
    print("-" * 40)

    try:
        config = get_config()

        # Check basic config
        print("✅ Configuration loaded successfully")
        print(f"   Environment: {config.environment}")
        print(f"   Debug mode: {config.debug}")
        print(f"   Log level: {config.log_level}")

        # Check Telegram config
        print(f"   Telegram API ID: {config.telegram.api_id}")
        print(f"   Session path: {config.telegram.session_path}")

        if config.telegram.api_id == 0 or not config.telegram.api_hash:
            print("⚠️  Warning: Telegram API credentials not configured")
            print("   This is expected if you haven't set up .env yet")
            return True
        else:
            print("✅ Telegram API credentials configured")
            return True

    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False


async def test_telegram_connection():
    """Test Telegram API connection."""
    print("\n📡 Testing Telegram API Connection")
    print("-" * 40)

    try:
        config = get_config()

        if config.telegram.api_id == 0 or not config.telegram.api_hash:
            print("⚠️  Skipping Telegram connection test - credentials not configured")
            print(
                "   Configure .env file with your Telegram API credentials to enable this test"
            )
            return True

        # Create client
        client = TelegramAnalyticsClient()
        await client.initialize()
        print("✅ Telegram client initialized")

        # Test connection
        if await client.connect():
            print("✅ Connected to Telegram servers")

            # Test authentication status
            if await client.is_authenticated():
                print("✅ User is authenticated")

                # Get user info
                me = await client.get_me()
                if me:
                    print(f"✅ User info retrieved: {me.first_name} (ID: {me.id})")
                else:
                    print("⚠️  Could not retrieve user info")
            else:
                print("ℹ️  User not authenticated (this is normal for first run)")
                print("   Run 'uv run python test_login.py' to authenticate")

            await client.disconnect()
            print("✅ Disconnected from Telegram")
            return True
        else:
            print("❌ Failed to connect to Telegram servers")
            return False

    except Exception as e:
        print(f"❌ Telegram connection test failed: {e}")
        return False


async def test_session_persistence():
    """Test session file handling."""
    print("\n💾 Testing Session Persistence")
    print("-" * 40)

    try:
        config = get_config()
        session_path = config.telegram.session_path

        print(f"Session file path: {session_path}")

        if session_path.exists():
            print("✅ Session file exists")
            file_size = session_path.stat().st_size
            print(f"   File size: {file_size} bytes")

            if file_size > 0:
                print("✅ Session file has content")
            else:
                print("⚠️  Session file is empty")
        else:
            print("ℹ️  Session file does not exist (normal for first run)")

        # Check session directory
        session_dir = session_path.parent
        if session_dir.exists():
            print(f"✅ Session directory exists: {session_dir}")
        else:
            print(f"⚠️  Session directory missing: {session_dir}")

        return True

    except Exception as e:
        print(f"❌ Session persistence test failed: {e}")
        return False


async def test_imports():
    """Test that all modules can be imported."""
    print("\n📦 Testing Module Imports")
    print("-" * 40)

    try:
        # Test core imports
        from telegram_analytics.core.config import TelegramConfig
        from telegram_analytics.core.client import (
            TelegramAnalyticsClient,
        )

        print("✅ Core modules imported successfully")

        # Test that classes can be instantiated
        config = TelegramConfig(api_id=123, api_hash="test")
        print("✅ TelegramConfig can be instantiated")

        TelegramAnalyticsClient(config)
        print("✅ TelegramAnalyticsClient can be instantiated")

        return True

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False


async def run_all_connectivity_tests():
    """Run all connectivity and integration tests."""
    print("🌐 Running Connectivity & Integration Tests")
    print("=" * 50)

    tests = [
        ("Module Imports", test_imports),
        ("Configuration Loading", test_config_loading),
        ("Session Persistence", test_session_persistence),
        ("Telegram Connection", test_telegram_connection),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 50)
    print("📊 CONNECTIVITY TEST SUMMARY")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    total = len(results)
    print(f"\nResults: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All connectivity tests passed!")
        return True
    else:
        print("⚠️  Some connectivity tests failed")
        return False


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Connectivity and integration tests for Telegram Analytics Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python test_connectivity.py           # Run all connectivity tests
  python test_connectivity.py --help    # Show this help
        """,
    )

    parser.parse_args()

    try:
        success = asyncio.run(run_all_connectivity_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test runner failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
