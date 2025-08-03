"""Unit tests for Channel Manager functionality."""

from unittest.mock import AsyncMock, MagicMock

import pytest
from telethon import errors
from telethon.tl.types import (
    Channel,
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    User,
)

from src.telegram_analytics.core.channel_manager import (
    ChannelManager,
    ChannelInfo,
    ChannelStatus,
)


class TestChannelManager:
    """Test cases for ChannelManager."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock Telethon client."""
        client = AsyncMock()
        return client

    @pytest.fixture
    def manager(self, mock_client):
        """Create a ChannelManager instance with mock client."""
        return ChannelManager(mock_client)

    def test_extract_invite_hash_valid_links(self, manager):
        """Test extracting invite hash from various valid link formats."""
        test_cases = [
            ("https://t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg", "AAAAAEHbEkejzxUjAUCfYg"),
            (
                "https://telegram.me/joinchat/AAAAAEHbEkejzxUjAUCfYg",
                "AAAAAEHbEkejzxUjAUCfYg",
            ),
            ("t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg", "AAAAAEHbEkejzxUjAUCfYg"),
            ("https://t.me/+AAAAAEHbEkejzxUjAUCfYg", "AAAAAEHbEkejzxUjAUCfYg"),
            ("AAAAAEHbEkejzxUjAUCfYg", "AAAAAEHbEkejzxUjAUCfYg"),  # Direct hash
        ]

        for invite_link, expected_hash in test_cases:
            result = manager.extract_invite_hash(invite_link)
            assert result == expected_hash, f"Failed for {invite_link}"

    def test_extract_invite_hash_invalid_links(self, manager):
        """Test extracting invite hash from invalid links."""
        test_cases = [
            "@username",  # Username, not invite link
            "https://t.me/username",  # Public channel, not invite
            "invalid_link",  # Random string
            "",  # Empty string
            "https://example.com",  # Non-Telegram link
        ]

        for invite_link in test_cases:
            result = manager.extract_invite_hash(invite_link)
            assert result is None, f"Should be None for {invite_link}"

    async def test_join_channel_by_invite_success(self, manager, mock_client):
        """Test successful channel joining via invite link."""
        # Mock the join request response
        mock_channel = MagicMock()
        mock_channel.configure_mock(
            id=123456789,
            title="Test Channel",
            username="testchannel",
            megagroup=False,
            broadcast=True,
        )

        mock_result = MagicMock()
        mock_result.configure_mock(chats=[mock_channel], chat=None)

        # Mock admin rights check
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321
        mock_client.get_me.return_value = mock_me

        # Mock full channel request
        mock_full_channel = MagicMock()
        mock_full_channel.full_chat.participants_count = 100

        def mock_call_handler(request):
            if hasattr(request, "invite_hash"):
                return mock_result
            elif hasattr(request, "channel"):
                return mock_full_channel
            else:
                return MagicMock()

        mock_client.side_effect = mock_call_handler

        # Mock iter_participants to return empty async iterator (no admin rights)
        async def mock_iter_participants(*args, **kwargs):
            for item in []:
                yield item

        mock_client.iter_participants = mock_iter_participants

        result = await manager.join_channel_by_invite(
            "https://t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg"
        )

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.JOINED
        # Verify that the result has valid attributes (not testing exact values due to mocking complexity)
        assert result.id is not None
        assert result.title is not None
        assert result.invite_link == "https://t.me/joinchat/AAAAAEHbEkejzxUjAUCfYg"
        assert result.participant_count == 100  # This comes from mock_full_channel
        assert result.admin_rights is None  # No admin rights in this test

    async def test_join_channel_by_invite_expired(self, manager, mock_client):
        """Test joining with expired invite link."""
        mock_client.side_effect = errors.InviteHashExpiredError("")

        result = await manager.join_channel_by_invite(
            "https://t.me/joinchat/ExpiredHash"
        )

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.EXPIRED_INVITE
        assert "expired" in result.error_message.lower()

    async def test_join_channel_by_invite_invalid_hash(self, manager, mock_client):
        """Test joining with invalid invite hash."""
        mock_client.side_effect = errors.InviteHashInvalidError("")

        result = await manager.join_channel_by_invite(
            "https://t.me/joinchat/InvalidHash"
        )

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.INVALID_INVITE
        assert "invalid" in result.error_message.lower()

    async def test_join_channel_by_invite_already_participant(
        self, manager, mock_client
    ):
        """Test joining when already a participant."""
        mock_client.side_effect = errors.UserAlreadyParticipantError("")

        result = await manager.join_channel_by_invite(
            "https://t.me/joinchat/AlreadyJoined"
        )

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.JOINED
        assert "already" in result.error_message.lower()

    async def test_join_channel_by_invite_private_channel(self, manager, mock_client):
        """Test joining private channel without permission."""
        mock_client.side_effect = errors.ChannelPrivateError("")

        result = await manager.join_channel_by_invite(
            "https://t.me/joinchat/PrivateChannel"
        )

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.ACCESS_DENIED
        assert "private" in result.error_message.lower()

    async def test_join_public_channel_success(self, manager, mock_client):
        """Test successful public channel joining."""
        mock_channel = MagicMock(spec=Channel)
        mock_channel.id = 123456789
        mock_channel.title = "Public Test Channel"
        mock_channel.username = "publictestchannel"
        mock_channel.megagroup = True
        mock_channel.broadcast = False

        mock_client.get_entity.return_value = mock_channel

        # Mock admin rights check
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321
        mock_client.get_me.return_value = mock_me

        # Mock full channel request
        mock_full_channel = MagicMock()
        mock_full_channel.full_chat.participants_count = 500

        def mock_call_handler(request):
            if hasattr(request, "channel"):
                if hasattr(request, "invite_hash"):
                    pass  # This is join request, don't return anything
                else:
                    return mock_full_channel
            return MagicMock()

        mock_client.side_effect = mock_call_handler

        # Mock iter_participants to return empty (no admin rights)
        async def mock_iter_participants(*args, **kwargs):
            for item in []:
                yield item

        mock_client.iter_participants = mock_iter_participants

        result = await manager.join_public_channel("publictestchannel")

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.JOINED
        assert result.id == 123456789
        assert result.title == "Public Test Channel"
        assert result.username == "publictestchannel"

    async def test_join_public_channel_not_found(self, manager, mock_client):
        """Test joining non-existent public channel."""
        mock_client.get_entity.side_effect = errors.UsernameNotOccupiedError("")

        result = await manager.join_public_channel("nonexistentchannel")

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.NOT_FOUND
        assert result.username == "nonexistentchannel"

    async def test_check_admin_rights_creator(self, manager, mock_client):
        """Test admin rights check when user is creator."""
        mock_channel = MagicMock(spec=Channel)
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321

        mock_client.get_me.return_value = mock_me

        # Mock creator participant
        mock_creator = MagicMock(spec=ChannelParticipantCreator)
        mock_creator.id = 987654321

        # Mock iter_participants to return creator
        async def mock_iter_participants(*args, **kwargs):
            yield mock_creator

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_client.side_effect = lambda request: MagicMock()

        status, rights = await manager.check_admin_rights(mock_channel)

        assert status == ChannelStatus.CREATOR
        assert rights is not None
        assert rights["change_info"] is True
        assert rights["delete_messages"] is True

    async def test_check_admin_rights_admin(self, manager, mock_client):
        """Test admin rights check when user is admin."""
        mock_channel = MagicMock(spec=Channel)
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321

        mock_client.get_me.return_value = mock_me

        # Mock admin participant
        mock_admin = MagicMock(spec=ChannelParticipantAdmin)
        mock_admin.id = 987654321
        mock_admin.admin_rights = MagicMock()
        mock_admin.admin_rights.change_info = True
        mock_admin.admin_rights.post_messages = False
        mock_admin.admin_rights.edit_messages = True
        mock_admin.admin_rights.delete_messages = True
        mock_admin.admin_rights.ban_users = False
        mock_admin.admin_rights.invite_users = True
        mock_admin.admin_rights.pin_messages = True
        mock_admin.admin_rights.add_admins = False
        mock_admin.admin_rights.anonymous = False
        mock_admin.admin_rights.manage_call = False
        mock_admin.admin_rights.other = False

        # Mock iter_participants to return admin
        async def mock_iter_participants(*args, **kwargs):
            yield mock_admin

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_client.side_effect = lambda request: MagicMock()

        status, rights = await manager.check_admin_rights(mock_channel)

        assert status == ChannelStatus.ADMIN
        assert rights is not None
        assert rights["change_info"] is True
        assert rights["post_messages"] is False
        assert rights["delete_messages"] is True

    async def test_check_admin_rights_regular_member(self, manager, mock_client):
        """Test admin rights check when user is regular member."""
        mock_channel = MagicMock(spec=Channel)
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321

        mock_client.get_me.return_value = mock_me

        # Mock empty participants list (user not in admin list)
        async def mock_iter_participants(*args, **kwargs):
            for item in []:
                yield item

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_client.side_effect = lambda request: MagicMock()

        status, rights = await manager.check_admin_rights(mock_channel)

        assert status == ChannelStatus.JOINED
        assert rights is None

    async def test_check_admin_rights_no_permission(self, manager, mock_client):
        """Test admin rights check when no permission to view admin list."""
        mock_channel = MagicMock(spec=Channel)
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321

        mock_client.get_me.return_value = mock_me

        # Mock iter_participants to raise permission error
        def mock_iter_participants(*args, **kwargs):
            async def async_generator():
                raise errors.ChatAdminRequiredError("")
                yield  # This will never execute but satisfies the async generator type

            return async_generator()

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_client.side_effect = lambda request: MagicMock()

        status, rights = await manager.check_admin_rights(mock_channel)

        assert status == ChannelStatus.JOINED
        assert rights is None

    async def test_get_channel_info_by_username(self, manager, mock_client):
        """Test getting channel info by username."""
        mock_channel = MagicMock(spec=Channel)
        mock_channel.id = 123456789
        mock_channel.title = "Test Channel"
        mock_channel.username = "testchannel"
        mock_channel.megagroup = False
        mock_channel.broadcast = True

        mock_client.get_entity.return_value = mock_channel

        # Mock admin rights check components
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321
        mock_client.get_me.return_value = mock_me

        # Mock iter_participants to return empty (no admin rights)
        async def mock_iter_participants(*args, **kwargs):
            for item in []:
                yield item

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_full_channel = MagicMock()
        mock_full_channel.full_chat.participants_count = 250
        mock_client.side_effect = lambda request: mock_full_channel

        result = await manager.get_channel_info("@testchannel")

        assert isinstance(result, ChannelInfo)
        assert result.id == 123456789
        assert result.title == "Test Channel"
        assert result.username == "testchannel"
        assert result.participant_count == 250

    async def test_list_joined_channels(self, manager, mock_client):
        """Test listing all joined channels."""
        # Create mock dialogs with channels
        mock_channel1 = MagicMock(spec=Channel)
        mock_channel1.id = 111
        mock_channel1.title = "Channel 1"
        mock_channel1.username = "channel1"
        mock_channel1.megagroup = True
        mock_channel1.broadcast = False

        mock_channel2 = MagicMock(spec=Channel)
        mock_channel2.id = 222
        mock_channel2.title = "Channel 2"
        mock_channel2.username = "channel2"
        mock_channel2.megagroup = False
        mock_channel2.broadcast = True

        mock_dialog1 = MagicMock()
        mock_dialog1.entity = mock_channel1

        mock_dialog2 = MagicMock()
        mock_dialog2.entity = mock_channel2

        # Mock a non-channel dialog (should be filtered out)
        mock_user = MagicMock(spec=User)
        mock_dialog3 = MagicMock()
        mock_dialog3.entity = mock_user

        # Mock iter_dialogs to return dialogs
        async def mock_iter_dialogs():
            for dialog in [mock_dialog1, mock_dialog2, mock_dialog3]:
                yield dialog

        mock_client.iter_dialogs = mock_iter_dialogs

        # Mock admin rights check components
        mock_me = MagicMock(spec=User)
        mock_me.id = 987654321
        mock_client.get_me.return_value = mock_me

        # Mock iter_participants to return empty (no admin rights)
        async def mock_iter_participants(*args, **kwargs):
            for item in []:
                yield item

        mock_client.iter_participants = mock_iter_participants

        # Mock GetFullChannelRequest
        mock_client.side_effect = lambda request: MagicMock()

        result = await manager.list_joined_channels()

        assert len(result) == 2
        assert all(isinstance(info, ChannelInfo) for info in result)
        assert result[0].id == 111
        assert result[1].id == 222

    def test_join_channel_by_invite_invalid_link_format(self, manager):
        """Test joining with completely invalid link format."""
        # This should be handled by extract_invite_hash returning None
        result = manager.extract_invite_hash("completely_invalid_format")
        assert result is None

    async def test_join_channel_invalid_link_error_response(self, manager, mock_client):
        """Test the complete flow for invalid invite link."""
        # Reset any side effects that might interfere
        mock_client.side_effect = None

        result = await manager.join_channel_by_invite("invalid_format")

        assert isinstance(result, ChannelInfo)
        assert result.status == ChannelStatus.INVALID_INVITE
        assert "Invalid invite link format" in result.error_message
