#!/usr/bin/env python3
"""Test script to verify Telethon authentication works."""

import asyncio
import logging
import sys

# Add src to path so we can import our modules
import os

src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from src.telegram_analytics.core.client import TelegramAnalyticsClient
from src.telegram_analytics.core.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


async def test_authentication():
    """Test Telegram authentication flow."""
    try:
        # Load configuration
        config = get_config()
        logger.info("Configuration loaded successfully")
        logger.info(f"API ID: {config.telegram.api_id}")
        logger.info(f"Session path: {config.telegram.session_path}")

        # Create client
        client = TelegramAnalyticsClient()
        await client.initialize()
        logger.info("Client initialized")

        # Connect to Telegram
        if not await client.connect():
            logger.error("Failed to connect to Telegram")
            return False

        # Check if already authenticated
        if await client.is_authenticated():
            logger.info("Already authenticated!")
            me = await client.get_me()
            if me:
                logger.info(
                    f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})"
                )
                logger.info(f"Phone: {me.phone}")
                logger.info(f"User ID: {me.id}")

                # Get session string for backup
                session_string = await client.get_session_string()
                if session_string:
                    logger.info(f"Session string: {session_string[:50]}...")

                return True
        else:
            logger.info("Not authenticated. Starting authentication process...")

            # Start authentication
            await client.authenticate()

    except RuntimeError as e:
        if "Code sent" in str(e):
            logger.info("✅ " + str(e))
            logger.info("\n📱 Verification code sent! To complete authentication:")
            logger.info("1. Check your phone/Telegram for the verification code")
            logger.info("2. Run: uv run python test_login.py --complete")
            logger.info("3. Enter the verification code when prompted")
            return True
        else:
            logger.error(f"Authentication test failed: {e}")
            return False
    except Exception as e:
        logger.error(f"Authentication test failed: {e}")
        return False
    finally:
        if "client" in locals():
            await client.disconnect()

    return False


async def complete_authentication():
    """Complete authentication with verification code."""
    try:
        config = get_config()

        # Get phone number and code from user
        phone = input(
            f"Enter phone number (default: {config.telegram.phone_number}): "
        ).strip()
        if not phone:
            phone = config.telegram.phone_number

        if not phone:
            logger.error("Phone number is required")
            return False

        code = input("Enter verification code: ").strip()
        if not code:
            logger.error("Verification code is required")
            return False

        password = input("Enter 2FA password (or press Enter if not enabled): ").strip()
        if not password:
            password = None

        # Create client and try to request code first (to get phone_code_hash)
        client = TelegramAnalyticsClient()
        await client.initialize()
        await client.connect()

        # Check if already authenticated
        if await client.is_authenticated():
            logger.info("Already authenticated!")
            me = await client.get_me()
            if me:
                logger.info(
                    f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})"
                )
            await client.disconnect()
            return True

        # Need to request a new code since we don't have the hash from previous session
        logger.info("Requesting new verification code...")
        try:
            await client.authenticate(phone)
        except RuntimeError as e:
            if "Code sent" in str(e):
                logger.info("✅ New code sent. Please check your phone.")
                # Get the new code
                new_code = input("Enter the new verification code: ").strip()
                if not new_code:
                    logger.error("Verification code is required")
                    return False
                code = new_code
            else:
                raise

        # Now sign in with the code
        if await client.sign_in(phone, code, password):
            logger.info("Successfully authenticated!")
            me = await client.get_me()
            if me:
                logger.info(
                    f"Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or 'No username'})"
                )
        else:
            logger.error("Authentication failed")
            return False

        await client.disconnect()
        return True

    except Exception as e:
        logger.error(f"Complete authentication failed: {e}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Test Telegram authentication")
    parser.add_argument(
        "--complete", action="store_true", help="Complete authentication with code"
    )
    args = parser.parse_args()

    if args.complete:
        success = asyncio.run(complete_authentication())
    else:
        success = asyncio.run(test_authentication())

    if success:
        logger.info("✅ Authentication test completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Authentication test failed!")
        sys.exit(1)
