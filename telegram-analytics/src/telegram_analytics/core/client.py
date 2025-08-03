"""Telethon client wrapper for Telegram Analytics."""

import logging
from typing import Optional, Any

from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.types import User

from .config import TelegramConfig, get_global_config

logger = logging.getLogger(__name__)


class TelegramAnalyticsClient:
    """Wrapper around Telethon client with analytics-specific functionality."""

    def __init__(self, telegram_config: Optional[TelegramConfig] = None):
        """Initialize the Telegram client.

        Args:
            telegram_config: Configuration object. If None, uses global config.
        """
        self.config = telegram_config or get_global_config().telegram
        self.client: Optional[TelegramClient] = None
        self._authenticated = False
        self._phone_code_hash: Optional[str] = None
        self._last_phone: Optional[str] = None

    async def initialize(self, session_string: Optional[str] = None) -> None:
        """Initialize the Telethon client.

        Args:
            session_string: Optional session string to resume existing session.
        """
        # Use session string if provided, otherwise use file-based session
        if session_string:
            session = StringSession(session_string)
        else:
            session = str(self.config.session_path)

        self.client = TelegramClient(
            session=session,
            api_id=self.config.api_id,
            api_hash=self.config.api_hash,
            device_model=self.config.device_model,
            system_version=self.config.system_version,
            app_version=self.config.app_version,
            lang_code=self.config.lang_code,
            system_lang_code=self.config.system_lang_code,
        )

        logger.info("Telegram client initialized")

    async def connect(self) -> bool:
        """Connect to Telegram.

        Returns:
            True if connected successfully, False otherwise.
        """
        if not self.client:
            await self.initialize()

        if self.client is None:
            logger.error("Client initialization failed")
            return False

        try:
            await self.client.connect()
            logger.info("Connected to Telegram")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Telegram: {e}")
            return False

    async def authenticate(
        self, phone_number: Optional[str] = None, force_sms: bool = False
    ) -> bool:
        """Authenticate with Telegram.

        Args:
            phone_number: Phone number for authentication. Uses config if not provided.
            force_sms: Force SMS code instead of calling.

        Returns:
            True if authenticated, False otherwise.
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        if not await self.client.is_user_authorized():
            phone = phone_number or self.config.phone_number
            if not phone:
                raise ValueError("Phone number is required for initial authentication")

            try:
                logger.info(f"Sending code request to {phone}")
                sent_code = await self.client.send_code_request(
                    phone, force_sms=force_sms
                )

                # Store the phone_code_hash for later use
                self._phone_code_hash = sent_code.phone_code_hash
                self._last_phone = phone

                # In production, you'd get this from user input
                # For now, we'll raise an exception to prompt for manual input
                logger.info(
                    f"Code sent to {phone}. Please call sign_in() with the received code."
                )
                raise RuntimeError(
                    f"Code sent to {phone}. Please call sign_in() with the received code."
                )

            except errors.PhoneNumberInvalidError:
                logger.error("Invalid phone number")
                return False
            except RuntimeError:
                # Re-raise RuntimeError for code request flow
                raise
            except Exception as e:
                logger.error(f"Authentication failed: {e}")
                return False
        else:
            logger.info("Already authenticated")
            self._authenticated = True
            return True

    async def sign_in(
        self, phone_number: str, code: str, password: Optional[str] = None
    ) -> bool:
        """Sign in with phone number and code.

        Args:
            phone_number: Phone number used for authentication.
            code: Verification code received via SMS/call.
            password: Two-factor authentication password if required.

        Returns:
            True if signed in successfully, False otherwise.
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        if not self._phone_code_hash:
            raise RuntimeError(
                "No phone_code_hash available. Call authenticate() first to request a code."
            )

        try:
            await self.client.sign_in(
                phone=phone_number,
                code=code,
                phone_code_hash=self._phone_code_hash,
                password=password,
            )
            self._authenticated = True
            logger.info("Successfully signed in to Telegram")

            # Clear the stored hash after successful authentication
            self._phone_code_hash = None
            self._last_phone = None

            return True
        except errors.PhoneCodeInvalidError:
            logger.error("Invalid verification code")
            return False
        except errors.PhoneCodeExpiredError:
            logger.error("Verification code expired")
            return False
        except errors.SessionPasswordNeededError:
            if not password:
                logger.error(
                    "Two-factor authentication required. Please provide password."
                )
                return False
            try:
                await self.client.sign_in(password=password)
                self._authenticated = True
                logger.info("Successfully signed in with 2FA")
                return True
            except errors.PasswordHashInvalidError:
                logger.error("Invalid 2FA password")
                return False
        except Exception as e:
            logger.error(f"Sign in failed: {e}")
            return False

    async def get_me(self) -> Optional[User]:
        """Get information about the authenticated user.

        Returns:
            User object if authenticated, None otherwise.
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Call initialize() first.")

        try:
            me = await self.client.get_me()
            logger.info(f"Authenticated as: {me.first_name} (@{me.username})")
            return me
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None

    async def get_session_string(self) -> Optional[str]:
        """Get session string for backup/transfer.

        Returns:
            Session string if available, None otherwise.
        """
        if not self.client:
            return None

        session = self.client.session
        if isinstance(session, StringSession):
            return str(session.save())
        return None

    async def is_authenticated(self) -> bool:
        """Check if client is authenticated.

        Returns:
            True if authenticated, False otherwise.
        """
        if not self.client:
            return False

        try:
            result = await self.client.is_user_authorized()
            return bool(result)
        except Exception:
            return False

    async def get_entity(self, entity: Any) -> Any:
        """Get entity information from Telegram.

        Args:
            entity: Username, phone, or entity ID.

        Returns:
            Entity object.
        """
        if not self.client:
            raise RuntimeError("Client not initialized")

        return await self.client.get_entity(entity)

    def iter_participants(self, entity: Any, **kwargs: Any) -> Any:
        """Iterate over participants in a chat.

        Args:
            entity: Chat entity.
            **kwargs: Additional arguments.

        Returns:
            Async iterator over participants.
        """
        if not self.client:
            raise RuntimeError("Client not initialized")

        return self.client.iter_participants(entity, **kwargs)

    def iter_dialogs(self, **kwargs: Any) -> Any:
        """Iterate over user's dialogs.

        Args:
            **kwargs: Additional arguments.

        Returns:
            Async iterator over dialogs.
        """
        if not self.client:
            raise RuntimeError("Client not initialized")

        return self.client.iter_dialogs(**kwargs)

    async def __call__(self, request: Any) -> Any:
        """Make a direct API call (delegate to underlying client).

        Args:
            request: Telegram API request object.

        Returns:
            API response.
        """
        if not self.client:
            raise RuntimeError("Client not initialized")

        return await self.client(request)

    async def disconnect(self) -> None:
        """Disconnect from Telegram."""
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected from Telegram")

    async def __aenter__(self) -> "TelegramAnalyticsClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None:
        """Async context manager exit."""
        await self.disconnect()


async def create_client(
    telegram_config: Optional[TelegramConfig] = None,
) -> TelegramAnalyticsClient:
    """Create and initialize a Telegram client.

    Args:
        telegram_config: Configuration object. If None, uses global config.

    Returns:
        Initialized TelegramAnalyticsClient instance.
    """
    client = TelegramAnalyticsClient(telegram_config)
    await client.initialize()
    return client
