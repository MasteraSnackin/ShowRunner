'''Utility helpers for the Showrunner agent.

The real implementation would likely use dependency‑injection frameworks, but for
this prototype we provide a few simple factory functions that create the
required objects on demand.
''' 

from __future__ import annotations

from typing import Any

from ..config import Settings
from ..logging_config import get_logger
from ..state_store import StateStore
from ..luffa.client import LuffaClient
from ..llm.client import LLMClient
from ..endless.client import EndlessClient
from ..civic.client import CivicClient

# Singletons – in a real app you might use a container or FastAPI Depends.
_logger = get_logger(__name__)
_settings = Settings()  # reads from .env or defaults
_state_store = StateStore(database_url=_settings.database_url)
_luffa_client = LuffaClient(base_url=_settings.luffa_base_url, api_key=_settings.luffa_api_key)
_llm_client = LLMClient()
_endless_client = EndlessClient()
_civic_client = CivicClient()


def get_logger_instance() -> Any:
    """Return the module‑level logger.

    The return type is ``Any`` to avoid pulling in the concrete ``logging.Logger``
    type which would add an import that is not required for the stub.
    """
    return _logger


def get_state_store() -> StateStore:
    return _state_store


def get_luffa_client() -> LuffaClient:
    return _luffa_client


def get_llm_client() -> LLMClient:
    return _llm_client


def get_endless_client() -> EndlessClient:
    return _endless_client


def get_civic_client() -> CivicClient:
    return _civic_client
