"""Configuration management for CTSR API."""

import os
from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env" if os.path.exists(".env") else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    postgres_host: str = Field(default="localhost")
    postgres_port: int = Field(default=5432)
    postgres_db: str = Field(default="ctsr")
    postgres_user: str = Field(default="ctsr_user")
    postgres_password: str = Field(default="ctsr_dev_password")
    database_url_override: str = Field(default="", alias="DATABASE_URL")
    test_database_url_override: str = Field(default="", alias="TEST_DATABASE_URL")

    # API
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_debug: bool = Field(default=False)

    # Azure AD Authentication
    azure_ad_enabled: bool = Field(default=False)
    azure_ad_tenant_id: str = Field(default="")
    azure_ad_client_id: str = Field(default="")
    azure_ad_audience: str = Field(default="")

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8501")

    # Logging
    log_level: str = Field(default="INFO")

    @property
    def database_url(self) -> str:
        """Build async PostgreSQL connection URL."""
        # Use TEST_DATABASE_URL if set (for testing), then DATABASE_URL, then build from components
        if self.test_database_url_override:
            return self.test_database_url_override
        if self.database_url_override:
            return self.database_url_override
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Ensure log level is valid."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}")
        return v_upper


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    # Clear cache in test environment to pick up TEST_DATABASE_URL
    if os.getenv("TEST_DATABASE_URL"):
        get_settings.cache_clear()
    return Settings()
