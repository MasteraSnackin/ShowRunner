'''LLM client stub.

In the real system this would call an LLM service (e.g. OpenAI) to generate a
human‑readable description of an event and optionally an image URL. For the
purposes of the hackathon we provide deterministic placeholder implementations
so that the rest of the code can be exercised without external dependencies.
''' 

from __future__ import annotations

import openai
from typing import Dict, Any

from ..config import Settings
from ..logging_config import get_logger


class LLMClient:
    """Wrapper around OpenAI's LLM services.

    Provides methods to generate a textual description and an image URL for an
    event using the configured OpenAI model and API key.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        # Configure OpenAI client
        openai.api_key = self.settings.OPENAI_API_KEY

    def generate_description(self, title: str, short_desc: str) -> str:
        """Generate a concise description for an event using ChatCompletion.

        Args:
            title: Event title.
            short_desc: Brief description provided by the user.
        Returns:
            A polished description string.
        """
        prompt = (
            f"Write a concise, engaging description for an event titled '{title}'. "
            f"Short description: {short_desc}."
        )
        response = openai.ChatCompletion.create(
            model=self.settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant that writes event descriptions."},
                {"role": "user", "content": prompt},
            ],
        )
        description = response.choices[0].message.content.strip()
        self.logger.debug("Generated description via OpenAI: %s", description)
        return description

    def generate_image_url(self, event: Any) -> str:
        """Generate an image URL for an event using OpenAI's Image API.

        Accepts either a string ``title`` or a dictionary with ``title`` and optional ``description``.
        Args:
            event: Either a title string or a dict containing ``title`` and ``description``.
        Returns:
            URL of the generated image, or an empty string on failure.
        """
        # Normalise input
        if isinstance(event, dict):
            title = event.get("title", "Event")
            desc = event.get("description", "")
        else:
            title = str(event)
            desc = ""
        prompt = f"Create a vivid banner image for an event titled '{title}'. {desc}"
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="1024x512",
            )
            url = response["data"][0]["url"]
            self.logger.debug("Generated image URL via OpenAI: %s", url)
            return url
        except Exception as exc:
            self.logger.error("OpenAI image generation failed: %s", exc)
            return ""
