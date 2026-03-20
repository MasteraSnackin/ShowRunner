'''Luffa HTTP client stub.

The real Luffa service provides a messaging API. For this prototype we
implement a thin wrapper around ``requests`` that sends JSON payloads to the
configured ``Luffa`` endpoint. The methods return the parsed JSON response.
''' 

from __future__ import annotations

import json
from typing import Any, Dict

import requests

from ..config import Settings
from ..logging_config import get_logger


class LuffaClient:
    """Simple HTTP client for the Luffa messaging platform.

    The client expects two environment variables defined in :class:`~app.config.Settings`:
    ``LUFFA_BASE_URL`` – the base URL of the Luffa API (e.g. ``https://api.luffa.ai``)
    ``LUFFA_TOKEN`` – a bearer token used for authentication.
    """

    def __init__(self, settings: Settings):
        self.base_url = settings.luffa_base_url.rstrip('/')
        self.token = settings.luffa_token
        self.logger = get_logger(self.__class__.__name__)
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        })

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/{path.lstrip('/')}"
        self.logger.debug("POST %s payload=%s", url, payload)
        response = self.session.post(url, json=payload)
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            self.logger.error("Luffa request failed: %s – %s", exc, response.text)
            raise
        try:
            data = response.json()
        except json.JSONDecodeError:
            self.logger.error("Luffa response not JSON: %s", response.text)
            raise
        self.logger.debug("Luffa response: %s", data)
        return data

    # ---------------------------------------------------------------------
    # Public API used by the orchestrator
    # ---------------------------------------------------------------------
    def send_message(self, channel_id: str, text: str) -> Dict[str, Any]:
        """Send a plain text message to *channel_id*.
        """
        payload = {"channel_id": channel_id, "text": text}
        return self._post("/messages", payload)

    def send_card(self, channel_id: str, title: str, description: str, image_url: str) -> Dict[str, Any]:
        """Send a rich card (title, description, image) to *channel_id*.
        """
        payload = {
            "channel_id": channel_id,
            "title": title,
            "description": description,
            "image_url": image_url,
        }
        return self._post("/cards", payload)
