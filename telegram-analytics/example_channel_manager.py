#!/usr/bin/env python3
"""Example script demonstrating ChannelManager usage."""

import asyncio
import logging

from src.telegram_analytics.core.channel_manager import ChannelManager, ChannelStatus

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Demonstrate ChannelManager functionality."""
    # This is just an example - you'll need real credentials
    print("=== Telegram Channel Analytics - ChannelManager Demo ===")
    print()
    print("This example demonstrates the ChannelManager functionality.")
    print("Note: This requires actual Telegram API credentials and authentication.")
    print()
    
    # Example 1: Extract invite hash from different link formats
    print("1. Extracting invite hashes from links:")
    
    # Create a dummy manager for demonstration (without client)
    from unittest.mock import MagicMock
    demo_manager = ChannelManager(MagicMock())
    
    test_links = [
        "https://t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg",
        "https://telegram.me/joinchat/BbBbBbEkejzxUjAUCfYg", 
        "t.me/joinchat/CcCcCcEkejzxUjAUCfYg",
        "https://t.me/+DdDdDdEkejzxUjAUCfYg",
        "@publicchannel",  # Invalid - username
        "invalid_link",    # Invalid - random text
    ]
    
    for link in test_links:
        hash_result = demo_manager.extract_invite_hash(link)
        status = "✅ Valid" if hash_result else "❌ Invalid"
        print(f"  {link:<50} → {status}")
        if hash_result:
            print(f"    Extracted hash: {hash_result}")
    
    print()
    print("2. Channel Management Operations:")
    print("   The following operations would be available with an authenticated client:")
    print()
    print("   📥 Join channel by invite link:")
    print("      result = await manager.join_channel_by_invite('https://t.me/joinchat/HASH')")
    print("      # Returns ChannelInfo with status, admin rights, participant count, etc.")
    print()
    print("   🔗 Join public channel:")
    print("      result = await manager.join_public_channel('publicchannel')")
    print()
    print("   🔍 Get channel information:")
    print("      info = await manager.get_channel_info('@channel_username')")
    print("      # Or by ID: await manager.get_channel_info('123456789')")
    print()
    print("   📋 List all joined channels:")
    print("      channels = await manager.list_joined_channels()")
    print()
    print("   👑 Check admin rights:")
    print("      status, rights = await manager.check_admin_rights(channel_entity)")
    print("      # Returns ChannelStatus and dict of admin permissions")
    print()
    
    print("3. ChannelStatus values:")
    for status in ChannelStatus:
        print(f"   • {status.value}: {status.name}")
    
    print()
    print("4. ChannelInfo fields:")
    print("   • id: Channel ID")
    print("   • title: Channel title")
    print("   • username: Channel username (if public)")
    print("   • participant_count: Number of members")
    print("   • is_megagroup: True for supergroups")
    print("   • is_broadcast: True for broadcast channels")
    print("   • status: ChannelStatus enum")
    print("   • invite_link: Original invite link (if used)")
    print("   • admin_rights: Dict of admin permissions (if admin)")
    print("   • error_message: Error details (if failed)")
    
    print()
    print("=== Example Usage with Real Client ===")
    print("""
# Example of real usage (requires authentication):

async def channel_management_example():
    from src.telegram_analytics.core.client import create_client
    from src.telegram_analytics.core.channel_manager import ChannelManager
    
    # Create and authenticate client
    client = await create_client()
    await client.connect()
    # ... authentication steps ...
    
    # Create channel manager
    manager = ChannelManager(client)
    
    # Join a channel
    result = await manager.join_channel_by_invite('https://t.me/joinchat/HASH')
    
    if result.status == ChannelStatus.JOINED:
        print(f"Successfully joined: {result.title}")
        print(f"Participants: {result.participant_count}")
        if result.admin_rights:
            print("Admin rights:", result.admin_rights)
    
    # List all channels
    channels = await manager.list_joined_channels()
    for channel in channels:
        print(f"- {channel.title} ({channel.status.value})")
    
    await client.disconnect()
""")


if __name__ == "__main__":
    asyncio.run(main())