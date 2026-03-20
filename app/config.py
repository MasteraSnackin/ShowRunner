'''Configuration module for Showrunner.

Defines a Pydantic ``BaseSettings`` class that reads all required
environment variables. The ``get_settings`` function returns a singleton
instance used throughout the code‑base.
'''

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import pathlib
import os
from typing import ClassVar


class Settings(BaseSettings):
    # Core FastAPI settings
    APP_ENV: str = Field("development")
    PORT: int = Field(8000)
    DATABASE_URL: str = Field("sqlite:///./showrunner.db")

    # Compatibility property for legacy code expecting lowercase attribute
    @property
    def database_url(self) -> str:
        """Return the database URL using the legacy attribute name.

        Some modules (e.g., `app.agent.tools`) still reference `_settings.database_url`.
        Providing this property maintains backward compatibility without altering the
        public Settings model.
        """
        return self.DATABASE_URL

    # Luffa integration
    LUFFA_API_BASE_URL: str = Field("https://dummy.luffa.api")
    LUFFA_API_TOKEN: str = Field("dummy-token")

    # Endless (blockchain) integration – stubbed
    ENDLESS_API_BASE_URL: str = Field("https://dummy.endless.api")
    ENDLESS_API_TOKEN: str = Field("dummy-token")

    # Civic (guardrails) integration – stubbed
    CIVIC_API_BASE_URL: str = Field("https://dummy.civic.api")
    CIVIC_API_TOKEN: str = Field("dummy-token")

    # LLM integration – stubbed
    LLM_API_BASE_URL: str = Field("https://dummy.llm.api")
    SECRET_KEY: str = Field("dummy-secret-key")
    OPENAI_API_KEY: str = Field("dummy-openai-key")
    OPENAI_MODEL: str = Field("gpt-4o-mini")

    # Compatibility properties for legacy attribute names expected by other modules
    @property
    def luffa_base_url(self) -> str:
        """Legacy alias for ``LUFFA_API_BASE_URL`` used by ``app.agent.tools``."""
        return self.LUFFA_API_BASE_URL

    @property
    def luffa_api_key(self) -> str:
        """Legacy alias for ``LUFFA_API_TOKEN`` used by ``app.agent.tools``."""
        return self.LUFFA_API_TOKEN

    @property
    def endless_base_url(self) -> str:
        """Legacy alias for ``ENDLESS_API_BASE_URL`` used by ``app.agent.tools``."""
        return self.ENDLESS_API_BASE_URL

    @property
    def endless_api_key(self) -> str:
        """Legacy alias for ``ENDLESS_API_TOKEN`` used by ``app.agent.tools``."""
        return self.ENDLESS_API_TOKEN

    @property
    def civic_base_url(self) -> str:
        """Legacy alias for ``CIVIC_API_BASE_URL`` used by ``app.agent.tools``."""
        return self.CIVIC_API_BASE_URL

    @property
    def civic_api_key(self) -> str:
        """Legacy alias for ``CIVIC_API_TOKEN`` used by ``app.agent.tools``."""
        return self.CIVIC_API_TOKEN

    # Additional legacy aliases for client constructors
    @property
    def luffa_token(self) -> str:
        """Alias for ``LUFFA_API_TOKEN`` used by ``LuffaClient``."""
        return self.LUFFA_API_TOKEN

    @property
    def endless_token(self) -> str:
        """Alias for ``ENDLESS_API_TOKEN`` used by ``EndlessClient``."""
        return self.ENDLESS_API_TOKEN

    @property
    def civic_token(self) -> str:
        """Alias for ``CIVIC_API_TOKEN`` used by ``CivicClient`` (if needed)."""
        return self.CIVIC_API_TOKEN

    @property
    def llm_api_key(self) -> str:
        """Alias for ``LLM_API_BASE_URL`` used by ``LLMClient`` (placeholder)."""
        return self.LLM_API_BASE_URL

    @property
    def llm_base_url(self) -> str:
        """Legacy alias for ``LLM_API_BASE_URL`` used by ``app.agent.tools`` (if needed)."""
        return self.LLM_API_BASE_URL

    # Payout configuration
    ORGANISER_ADDRESS: str = Field("0xOrganizerDummy")
    TREASURY_ADDRESS: str = Field("0xTreasuryDummy")
    ORGANISER_SHARE: float = Field(0.9)
    TREASURY_SHARE: float = Field(0.1)

    # Allow overriding the .env path via ENV_PATH environment variable for flexibility in different deployment scenarios.
    ENV_PATH: ClassVar[pathlib.Path] = pathlib.Path(os.getenv("ENV_PATH", pathlib.Path(__file__).resolve().parents[1] / "showrunner" / ".env"))
    model_config = SettingsConfigDict(env_file=ENV_PATH, env_file_encoding="utf-8")
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
