#!/usr/bin/env python3
"""Production test for channel management features.

This script tests channel management with real Telegram API calls.
It is intentionally separate from the unit tests because:
- It requires real Telegram authentication
- It makes actual API calls (not safe for CI/CD)
- It's not deterministic (depends on real channel data)

Use this script to manually verify channel management works in production.
"""

import asyncio
import logging

from telegram_analytics.core.client import create_client
from telegram_analytics.core.channel_manager import ChannelManager, ChannelStatus

logging.basicConfig(level=logging.INFO)


async def test_channel_management():
    """Test channel management with real Telegram API."""
    print("🚀 Testing Channel Management in Production")
    print("=" * 50)

    # Create and connect client
    client = await create_client()
    await client.connect()

    if not await client.is_authenticated():
        print("❌ Not authenticated! Run 'make auth-setup' first.")
        return

    print("✅ Authenticated successfully!")
    me = await client.get_me()
    print(f"👤 Logged in as: {me.first_name} (@{me.username or 'no_username'})")

    # Create channel manager
    manager = ChannelManager(client)

    print("\n📺 Testing Channel Operations...")

    # Test 1: Join official Telegram channel (safe)
    print("\n1️⃣ Testing public channel join...")
    result = await manager.join_public_channel("telegram")
    print(f"   Status: {result.status.value}")
    print(f"   Channel: {result.title}")
    member_count = (
        result.participant_count if result.participant_count is not None else "Unknown"
    )
    if isinstance(member_count, int):
        print(f"   Members: {member_count:,}")
    else:
        print(f"   Members: {member_count}")
    if result.admin_rights:
        print(f"   Admin rights: {list(result.admin_rights.keys())}")

    # Test 2: List all channels you're in
    print("\n2️⃣ Listing all joined channels...")
    channels = await manager.list_joined_channels()
    print(f"   Found {len(channels)} channels:")
    for i, channel in enumerate(channels[:5], 1):  # Show first 5
        status_icon = (
            "👑"
            if channel.status == ChannelStatus.CREATOR
            else "⭐" if channel.status == ChannelStatus.ADMIN else "👥"
        )
        member_count = (
            channel.participant_count
            if channel.participant_count is not None
            else "Unknown"
        )
        if isinstance(member_count, int):
            print(f"   {i}. {status_icon} {channel.title} ({member_count:,} members)")
        else:
            print(f"   {i}. {status_icon} {channel.title} ({member_count} members)")
    if len(channels) > 5:
        print(f"   ... and {len(channels) - 5} more")

    # Test 3: Get detailed info for a channel
    if channels:
        print("\n3️⃣ Getting detailed channel info...")
        test_channel = channels[0]
        status, rights = await manager.check_admin_rights(test_channel.id)
        print(f"   Channel: {test_channel.title}")
        print(f"   Your status: {status.value}")
        if rights:
            print(f"   Admin permissions: {rights}")

    # Test 4: Test invite link parsing (safe)
    print("\n4️⃣ Testing invite link parsing...")
    test_links = [
        "https://t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg",
        "https://t.me/+BbBbBbEkejzxUjAUCfYg",
        "@telegram",
        "invalid_link",
    ]
    for link in test_links:
        hash_result = manager.extract_invite_hash(link)
        status = "✅ Valid" if hash_result else "❌ Invalid"
        print(f"   {link} → {status}")
        if hash_result:
            print(f"      Hash: {hash_result}")

    print("\n✅ All tests completed!")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(test_channel_management())
