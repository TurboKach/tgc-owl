"""Configuration settings for Telegram Analytics using Pydantic."""

from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramConfig(BaseSettings):
    """Telegram API configuration."""

    # Telegram API credentials (get from https://my.telegram.org)
    api_id: int = Field(default=0, description="Telegram API ID")
    api_hash: str = Field(default="", description="Telegram API Hash")

    # Session configuration
    session_name: str = Field(
        default="telegram_analytics", description="Session file name"
    )
    session_dir: Path = Field(
        default_factory=lambda: Path("sessions"),
        description="Directory to store session files",
    )

    # Optional phone number for initial auth
    phone_number: Optional[str] = Field(
        default=None, description="Phone number for userbot authentication"
    )

    # Security settings
    device_model: str = Field(
        default="Telegram Analytics Bot", description="Device model for session"
    )
    system_version: str = Field(default="1.0", description="System version for session")
    app_version: str = Field(default="1.0.0", description="App version for session")
    lang_code: str = Field(default="en", description="Language code")
    system_lang_code: str = Field(default="en", description="System language code")

    @field_validator("session_dir")
    @classmethod
    def create_session_dir(cls, v: Path) -> Path:
        """Ensure session directory exists."""
        v.mkdir(exist_ok=True, parents=True)
        return v

    @property
    def session_path(self) -> Path:
        """Full path to session file."""
        return self.session_dir / f"{self.session_name}.session"

    model_config = SettingsConfigDict(
        env_prefix="TELEGRAM_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class DatabaseConfig(BaseSettings):
    """Database configuration."""

    host: str = Field(default="localhost", description="Database host")
    port: int = Field(default=5432, description="Database port")
    name: str = Field(default="telegram_analytics", description="Database name")
    user: str = Field(default="postgres", description="Database user")
    password: str = Field(default="", description="Database password")

    @property
    def url(self) -> str:
        """Database URL for SQLAlchemy."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

    model_config = SettingsConfigDict(
        env_prefix="DATABASE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


class AppConfig(BaseSettings):
    """Main application configuration."""

    # Environment
    environment: str = Field(
        default="development", description="Application environment"
    )
    debug: bool = Field(default=True, description="Debug mode")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: Optional[Path] = Field(default=None, description="Log file path")

    # API settings
    api_host: str = Field(default="localhost", description="API host")
    api_port: int = Field(default=8000, description="API port")

    # Security
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24 * 7, description="Access token expiration in minutes"
    )

    # Telegram and Database configs
    telegram: TelegramConfig = Field(default_factory=TelegramConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        allowed = {"development", "testing", "production"}
        if v not in allowed:
            raise ValueError(f"Environment must be one of {allowed}")
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )


def get_config() -> AppConfig:
    """Get application configuration instance."""
    return AppConfig()


# Global config instance - only create when explicitly needed
config = None


def get_global_config() -> AppConfig:
    """Get or create global configuration instance."""
    global config
    if config is None:
        config = get_config()
    return config
