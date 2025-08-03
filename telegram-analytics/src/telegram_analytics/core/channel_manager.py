"""Channel management functionality for Telegram Analytics."""

import logging
import re
from typing import Optional, Dict, List
from dataclasses import dataclass
from enum import Enum

from telethon import TelegramClient, errors
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest, GetFullChannelRequest
from telethon.tl.types import (
    Channel,
    ChannelParticipantAdmin,
    ChannelParticipantCreator,
    ChannelParticipantsAdmins,
)

logger = logging.getLogger(__name__)


class ChannelStatus(Enum):
    """Channel connection status."""

    NOT_JOINED = "not_joined"
    JOINED = "joined"
    ADMIN = "admin"
    CREATOR = "creator"
    ACCESS_DENIED = "access_denied"
    NOT_FOUND = "not_found"
    INVALID_INVITE = "invalid_invite"
    EXPIRED_INVITE = "expired_invite"


@dataclass
class ChannelInfo:
    """Channel information container."""

    id: int
    title: str
    username: Optional[str]
    participant_count: Optional[int]
    is_megagroup: bool
    is_broadcast: bool
    status: ChannelStatus
    invite_link: Optional[str] = None
    admin_rights: Optional[Dict[str, bool]] = None
    error_message: Optional[str] = None


class ChannelManager:
    """Manages channel operations for Telegram Analytics."""

    def __init__(self, client: TelegramClient):
        """Initialize channel manager.

        Args:
            client: Authenticated Telethon client instance.
        """
        self.client = client
        self._invite_link_pattern = re.compile(
            r"(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/(?:joinchat/|[+])([A-Za-z0-9_-]+)"
        )

    def extract_invite_hash(self, invite_link: str) -> Optional[str]:
        """Extract invite hash from Telegram invite link.

        Args:
            invite_link: Telegram invite link (t.me/joinchat/HASH or @username).

        Returns:
            Invite hash if found, None otherwise.
        """
        # Handle different invite link formats
        invite_link = invite_link.strip()

        # Remove @ prefix if present
        if invite_link.startswith("@"):
            return None  # This is a username, not an invite link

        # Match invite link patterns
        match = self._invite_link_pattern.search(invite_link)
        if match:
            return match.group(1)

        # Direct hash (fallback) - must be alphanumeric, reasonable length, and look like base64
        if (
            len(invite_link) >= 20
            and len(invite_link) <= 50
            and not invite_link.startswith("http")
            and " " not in invite_link
            and invite_link.replace("-", "").replace("_", "").isalnum()
            and
            # Should look like a base64-encoded string (mixed case and/or numbers)
            any(c.isupper() for c in invite_link)
            and any(c.islower() for c in invite_link)
        ):
            return invite_link

        return None

    async def join_channel_by_invite(self, invite_link: str) -> ChannelInfo:
        """Join a channel using an invite link.

        Args:
            invite_link: Telegram invite link or hash.

        Returns:
            ChannelInfo object with join status and details.
        """
        logger.info(f"Attempting to join channel via invite: {invite_link}")

        # Extract invite hash
        invite_hash = self.extract_invite_hash(invite_link)
        if not invite_hash:
            logger.error(f"Invalid invite link format: {invite_link}")
            return ChannelInfo(
                id=0,
                title="Unknown",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.INVALID_INVITE,
                invite_link=invite_link,
                error_message="Invalid invite link format",
            )

        try:
            # Import chat invite (join the channel)
            result = await self.client(ImportChatInviteRequest(invite_hash))

            # Extract channel from updates
            chat = None
            if hasattr(result, "chats") and result.chats:
                chat = result.chats[0]
            elif hasattr(result, "chat"):
                chat = result.chat

            if not chat:
                logger.error("No chat found in join result")
                return ChannelInfo(
                    id=0,
                    title="Unknown",
                    username=None,
                    participant_count=None,
                    is_megagroup=False,
                    is_broadcast=False,
                    status=ChannelStatus.NOT_FOUND,
                    invite_link=invite_link,
                    error_message="Channel not found in join result",
                )

            # Get channel info and admin status
            channel_info = await self._build_channel_info(chat, invite_link)
            logger.info(
                f"Successfully joined channel: {channel_info.title} (ID: {channel_info.id})"
            )

            return channel_info

        except errors.InviteHashExpiredError:
            logger.error(f"Invite link expired: {invite_link}")
            return ChannelInfo(
                id=0,
                title="Unknown",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.EXPIRED_INVITE,
                invite_link=invite_link,
                error_message="Invite link has expired",
            )

        except errors.InviteHashInvalidError:
            logger.error(f"Invalid invite hash: {invite_link}")
            return ChannelInfo(
                id=0,
                title="Unknown",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.INVALID_INVITE,
                invite_link=invite_link,
                error_message="Invalid invite hash",
            )

        except errors.UserAlreadyParticipantError:
            logger.info(f"Already a participant of the channel: {invite_link}")
            # Try to get channel info via the invite hash or by searching
            try:
                # This is a bit tricky - we need to find the channel we're already in
                # For now, return a basic response indicating we're already joined
                return ChannelInfo(
                    id=0,
                    title="Already Joined",
                    username=None,
                    participant_count=None,
                    is_megagroup=False,
                    is_broadcast=False,
                    status=ChannelStatus.JOINED,
                    invite_link=invite_link,
                    error_message="Already a participant - channel info unavailable",
                )
            except Exception as e:
                logger.error(f"Failed to get info for already joined channel: {e}")
                return ChannelInfo(
                    id=0,
                    title="Already Joined",
                    username=None,
                    participant_count=None,
                    is_megagroup=False,
                    is_broadcast=False,
                    status=ChannelStatus.JOINED,
                    invite_link=invite_link,
                    error_message=f"Already joined but couldn't fetch details: {str(e)}",
                )

        except errors.ChannelPrivateError:
            logger.error(f"Channel is private and inaccessible: {invite_link}")
            return ChannelInfo(
                id=0,
                title="Private Channel",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.ACCESS_DENIED,
                invite_link=invite_link,
                error_message="Channel is private",
            )

        except Exception as e:
            logger.error(f"Failed to join channel {invite_link}: {e}")
            return ChannelInfo(
                id=0,
                title="Unknown",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.NOT_FOUND,
                invite_link=invite_link,
                error_message=f"Join failed: {str(e)}",
            )

    async def join_public_channel(self, username: str) -> ChannelInfo:
        """Join a public channel by username.

        Args:
            username: Channel username (with or without @).

        Returns:
            ChannelInfo object with join status and details.
        """
        # Clean username
        username = username.lstrip("@")
        logger.info(f"Attempting to join public channel: @{username}")

        try:
            # Get channel entity first
            channel = await self.client.get_entity(username)

            # Join the channel
            await self.client(JoinChannelRequest(channel))

            # Get channel info and admin status
            channel_info = await self._build_channel_info(channel)
            logger.info(
                f"Successfully joined public channel: {channel_info.title} (ID: {channel_info.id})"
            )

            return channel_info

        except errors.UsernameNotOccupiedError:
            logger.error(f"Username not found: @{username}")
            return ChannelInfo(
                id=0,
                title=f"@{username}",
                username=username,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.NOT_FOUND,
                error_message="Username not found",
            )

        except errors.UserAlreadyParticipantError:
            logger.info(f"Already a participant of @{username}")
            try:
                channel = await self.client.get_entity(username)
                channel_info = await self._build_channel_info(channel)
                return channel_info
            except Exception as e:
                logger.error(
                    f"Failed to get info for already joined channel @{username}: {e}"
                )
                return ChannelInfo(
                    id=0,
                    title=f"@{username}",
                    username=username,
                    participant_count=None,
                    is_megagroup=False,
                    is_broadcast=False,
                    status=ChannelStatus.JOINED,
                    error_message=f"Already joined but couldn't fetch details: {str(e)}",
                )

        except Exception as e:
            logger.error(f"Failed to join public channel @{username}: {e}")
            return ChannelInfo(
                id=0,
                title=f"@{username}",
                username=username,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.NOT_FOUND,
                error_message=f"Join failed: {str(e)}",
            )

    async def check_admin_rights(
        self, channel_entity: Channel
    ) -> tuple[ChannelStatus, Optional[Dict[str, bool]]]:
        """Check if userbot has admin rights in a channel.

        Args:
            channel_entity: Channel entity object.

        Returns:
            Tuple of (status, admin_rights_dict).
        """
        try:
            # Get current user info
            me = await self.client.get_me()

            # Get full channel info to access participant list
            await self.client(GetFullChannelRequest(channel_entity))

            # Check if we can get participants (admin permission needed)
            try:
                async for participant in self.client.iter_participants(
                    channel_entity, filter=ChannelParticipantsAdmins
                ):
                    if participant.id == me.id:
                        if isinstance(participant, ChannelParticipantCreator):
                            return ChannelStatus.CREATOR, {
                                "change_info": True,
                                "post_messages": True,
                                "edit_messages": True,
                                "delete_messages": True,
                                "ban_users": True,
                                "invite_users": True,
                                "pin_messages": True,
                                "add_admins": True,
                                "anonymous": getattr(
                                    participant, "admin_rights", {}
                                ).get("anonymous", False),
                                "manage_call": True,
                                "other": True,
                            }
                        elif isinstance(participant, ChannelParticipantAdmin):
                            rights = participant.admin_rights
                            return ChannelStatus.ADMIN, {
                                "change_info": rights.change_info,
                                "post_messages": rights.post_messages,
                                "edit_messages": rights.edit_messages,
                                "delete_messages": rights.delete_messages,
                                "ban_users": rights.ban_users,
                                "invite_users": rights.invite_users,
                                "pin_messages": rights.pin_messages,
                                "add_admins": rights.add_admins,
                                "anonymous": rights.anonymous,
                                "manage_call": rights.manage_call,
                                "other": rights.other,
                            }

                # If we reach here, we're not an admin
                return ChannelStatus.JOINED, None

            except errors.ChatAdminRequiredError:
                # We don't have permission to view admin list, so we're just a regular member
                return ChannelStatus.JOINED, None

        except Exception as e:
            logger.error(f"Failed to check admin rights: {e}")
            return ChannelStatus.JOINED, None

    async def _build_channel_info(
        self, channel_entity: Channel, invite_link: Optional[str] = None
    ) -> ChannelInfo:
        """Build ChannelInfo from channel entity.

        Args:
            channel_entity: Channel entity object.
            invite_link: Original invite link if available.

        Returns:
            ChannelInfo object.
        """
        try:
            # Check admin rights
            status, admin_rights = await self.check_admin_rights(channel_entity)

            # Get additional channel details
            participant_count = None
            try:
                full_channel = await self.client(GetFullChannelRequest(channel_entity))
                participant_count = full_channel.full_chat.participants_count
            except Exception as e:
                logger.warning(f"Could not get participant count: {e}")

            return ChannelInfo(
                id=channel_entity.id,
                title=channel_entity.title,
                username=getattr(channel_entity, "username", None),
                participant_count=participant_count,
                is_megagroup=getattr(channel_entity, "megagroup", False),
                is_broadcast=getattr(channel_entity, "broadcast", False),
                status=status,
                invite_link=invite_link,
                admin_rights=admin_rights,
            )

        except Exception as e:
            logger.error(f"Failed to build channel info: {e}")
            return ChannelInfo(
                id=getattr(channel_entity, "id", 0),
                title=getattr(channel_entity, "title", "Unknown"),
                username=getattr(channel_entity, "username", None),
                participant_count=None,
                is_megagroup=getattr(channel_entity, "megagroup", False),
                is_broadcast=getattr(channel_entity, "broadcast", False),
                status=ChannelStatus.JOINED,
                invite_link=invite_link,
                error_message=f"Failed to get full channel details: {str(e)}",
            )

    async def get_channel_info(self, channel_identifier: str) -> ChannelInfo:
        """Get information about a channel by identifier.

        Args:
            channel_identifier: Channel username, ID, or invite link.

        Returns:
            ChannelInfo object.
        """
        try:
            # Try to get the channel entity
            if channel_identifier.startswith("@"):
                # Username
                channel_entity = await self.client.get_entity(channel_identifier)
            elif channel_identifier.isdigit() or (
                channel_identifier.startswith("-") and channel_identifier[1:].isdigit()
            ):
                # Numeric ID
                channel_entity = await self.client.get_entity(int(channel_identifier))
            elif "joinchat" in channel_identifier or "t.me" in channel_identifier:
                # This is an invite link - we need to join first to get info
                return await self.join_channel_by_invite(channel_identifier)
            else:
                # Try as username without @
                channel_entity = await self.client.get_entity(channel_identifier)

            return await self._build_channel_info(channel_entity)

        except Exception as e:
            logger.error(f"Failed to get channel info for {channel_identifier}: {e}")
            return ChannelInfo(
                id=0,
                title="Unknown",
                username=None,
                participant_count=None,
                is_megagroup=False,
                is_broadcast=False,
                status=ChannelStatus.NOT_FOUND,
                error_message=f"Failed to get channel info: {str(e)}",
            )

    async def list_joined_channels(self) -> List[ChannelInfo]:
        """List all channels the userbot has joined.

        Returns:
            List of ChannelInfo objects for joined channels.
        """
        channels = []

        try:
            async for dialog in self.client.iter_dialogs():
                entity = dialog.entity

                # Only include channels (not private chats or regular groups)
                if isinstance(entity, Channel):
                    channel_info = await self._build_channel_info(entity)
                    channels.append(channel_info)

        except Exception as e:
            logger.error(f"Failed to list joined channels: {e}")

        return channels
