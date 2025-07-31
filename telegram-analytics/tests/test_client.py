"""Unit tests for Telegram client functionality."""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from src.telegram_analytics.core.client import TelegramAnalyticsClient
from src.telegram_analytics.core.config import TelegramConfig


class TestTelegramAnalyticsClient:
    """Test cases for TelegramAnalyticsClient."""

    @pytest.fixture
    def mock_config(self):
        """Create a mock Telegram configuration."""
        config = TelegramConfig(
            api_id=123456,
            api_hash="test_hash",
            phone_number="+1234567890",
            session_name="test_session",
            session_dir=Path("test_sessions"),
        )
        return config

    @pytest.fixture
    def client(self, mock_config):
        """Create a TelegramAnalyticsClient instance with mock config."""
        return TelegramAnalyticsClient(mock_config)

    def test_client_initialization(self, client, mock_config):
        """Test client initialization."""
        assert client.config == mock_config
        assert client.client is None
        assert not client._authenticated

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_initialize(self, mock_telegram_client, client):
        """Test client initialization."""
        await client.initialize()

        assert client.client is not None
        mock_telegram_client.assert_called_once()

        # Check that TelegramClient was called with correct parameters
        call_args = mock_telegram_client.call_args
        assert call_args[1]["api_id"] == 123456
        assert call_args[1]["api_hash"] == "test_hash"

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_connect_success(self, mock_telegram_client, client):
        """Test successful connection."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.connect.return_value = True

        await client.initialize()
        result = await client.connect()

        assert result is True
        mock_client.connect.assert_called_once()

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_connect_failure(self, mock_telegram_client, client):
        """Test connection failure."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.connect.side_effect = Exception("Connection failed")

        await client.initialize()
        result = await client.connect()

        assert result is False
        mock_client.connect.assert_called_once()

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_is_authenticated(self, mock_telegram_client, client):
        """Test authentication check."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.is_user_authorized.return_value = True

        await client.initialize()
        result = await client.is_authenticated()

        assert result is True
        mock_client.is_user_authorized.assert_called_once()

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_authenticate_already_authorized(self, mock_telegram_client, client):
        """Test authentication when already authorized."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.is_user_authorized.return_value = True

        await client.initialize()
        result = await client.authenticate()

        assert result is True
        assert client._authenticated is True

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_authenticate_code_request(self, mock_telegram_client, client):
        """Test authentication code request."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.is_user_authorized.return_value = False
        mock_client.send_code_request.return_value = MagicMock()

        await client.initialize()

        with pytest.raises(RuntimeError, match="Code sent"):
            await client.authenticate("+1234567890")

        mock_client.send_code_request.assert_called_once_with(
            "+1234567890", force_sms=False
        )

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_sign_in_success(self, mock_telegram_client, client):
        """Test successful sign in."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client
        mock_client.sign_in.return_value = MagicMock()

        await client.initialize()

        # Set up phone_code_hash (normally set by authenticate())
        client._phone_code_hash = "test_hash"

        result = await client.sign_in("+1234567890", "12345")

        assert result is True
        assert client._authenticated is True
        mock_client.sign_in.assert_called_once_with(
            phone="+1234567890",
            code="12345",
            phone_code_hash="test_hash",
            password=None,
        )

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_get_me_success(self, mock_telegram_client, client):
        """Test getting user information."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client

        mock_user = MagicMock()
        mock_user.first_name = "Test"
        mock_user.username = "testuser"
        mock_client.get_me.return_value = mock_user

        await client.initialize()
        result = await client.get_me()

        assert result == mock_user
        mock_client.get_me.assert_called_once()

    @patch("telegram_analytics.core.client.TelegramClient")
    async def test_disconnect(self, mock_telegram_client, client):
        """Test disconnection."""
        mock_client = AsyncMock()
        mock_telegram_client.return_value = mock_client

        await client.initialize()
        await client.disconnect()

        mock_client.disconnect.assert_called_once()

    async def test_context_manager(self):
        """Test async context manager functionality."""
        with patch(
            "telegram_analytics.core.client.TelegramClient"
        ) as mock_telegram_client:
            mock_client = AsyncMock()
            mock_telegram_client.return_value = mock_client
            mock_client.connect.return_value = True

            config = TelegramConfig(api_id=123456, api_hash="test_hash")

            async with TelegramAnalyticsClient(config) as client:
                assert client.client is not None
                mock_client.connect.assert_called_once()

            mock_client.disconnect.assert_called_once()


class TestTelegramConfigValidation:
    """Test configuration validation."""

    def test_valid_config(self):
        """Test valid configuration creation."""
        config = TelegramConfig(api_id=123456, api_hash="valid_hash")
        assert config.api_id == 123456
        assert config.api_hash == "valid_hash"
        assert config.session_name == "telegram_analytics"

    def test_session_path_property(self):
        """Test session path property."""
        config = TelegramConfig(
            api_id=123456,
            api_hash="test_hash",
            session_name="test_session",
            session_dir=Path("test_dir"),
        )
        expected_path = Path("test_dir") / "test_session.session"
        assert config.session_path == expected_path
