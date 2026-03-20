'''Configuration module for Showrunner.

Defines a Pydantic ``BaseSettings`` class that reads all required
environment variables. The ``get_settings`` function returns a singleton
instance used throughout the code‑base.
'''

from __future__ import annotations

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    # Core FastAPI settings
    APP_ENV: str = Field("development", env="APP_ENV")
    PORT: int = Field(8000, env="PORT")
    DATABASE_URL: str = Field("sqlite:///./showrunner.db", env="DATABASE_URL")

    # Luffa integration
    LUFFA_API_BASE_URL: str = Field(..., env="LUFFA_API_BASE_URL")
    LUFFA_API_TOKEN: str = Field(..., env="LUFFA_API_TOKEN")

    # Endless (blockchain) integration – stubbed
    ENDLESS_API_BASE_URL: str = Field(..., env="ENDLESS_API_BASE_URL")
    ENDLESS_API_TOKEN: str = Field(..., env="ENDLESS_API_TOKEN")

    # Civic (guardrails) integration – stubbed
    CIVIC_API_BASE_URL: str = Field(..., env="CIVIC_API_BASE_URL")
    CIVIC_API_TOKEN: str = Field(..., env="CIVIC_API_TOKEN")

    # LLM integration – stubbed
    LLM_API_BASE_URL: str = Field(..., env="LLM_API_BASE_URL")

    # Payout configuration
    ORGANISER_ADDRESS: str = Field(..., env="ORGANISER_ADDRESS")
    TREASURY_ADDRESS: str = Field(..., env="TREASURY_ADDRESS")
    ORGANISER_SHARE: float = Field(0.9, env="ORGANISER_SHARE")
    TREASURY_SHARE: float = Field(0.1, env="TREASURY_SHARE")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Simple singleton pattern – the Settings instance is created once and reused.
_settings: Settings | None = None


def get_settings() -> Settings:
    """Return a cached Settings instance.

    The first call creates the ``Settings`` object, subsequent calls return the
    same instance. This avoids repeated parsing of the ``.env`` file.
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
