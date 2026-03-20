'''LLM client stub.

In the real system this would call an LLM service (e.g. OpenAI) to generate a
human-readable description of an event and optionally an image URL. For the
purposes of the hackathon we provide deterministic placeholder implementations
so that the rest of the code can be exercised without external dependencies.
'''

from __future__ import annotations

from typing import Any

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - exercised in local dev environments
    OpenAI = None

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
        self.client = OpenAI(api_key=self.settings.OPENAI_API_KEY) if OpenAI else None

    def _fallback_description(self, title: str, short_desc: str) -> str:
        base = short_desc.strip() or "No description provided."
        return f"{title}: {base}"

    def generate_description(self, title: str, short_desc: str) -> str:
        """Generate a concise description for an event.

        Args:
            title: Event title.
            short_desc: Brief description provided by the user.
        Returns:
            A polished description string.
        """
        if not self.client or not self.settings.OPENAI_API_KEY or self.settings.OPENAI_API_KEY == "dummy-openai-key":
            return self._fallback_description(title, short_desc)

        prompt = (
            f"Write a concise, engaging description for an event titled '{title}'. "
            f"Short description: {short_desc}."
        )
        try:
            response = self.client.responses.create(
                model=self.settings.OPENAI_MODEL,
                input=[
                    {"role": "system", "content": "You are an assistant that writes event descriptions."},
                    {"role": "user", "content": prompt},
                ],
            )
            description = (response.output_text or "").strip()
            return description or self._fallback_description(title, short_desc)
        except Exception as exc:  # pragma: no cover - networked provider errors are environment-specific
            self.logger.warning("OpenAI description generation failed, using fallback: %s", exc)
            return self._fallback_description(title, short_desc)

    def generate_image_url(self, event: Any) -> str:
        """Generate an image URL for an event.

        Accepts either a string ``title`` or a dictionary with ``title`` and optional ``description``.
        Args:
            event: Either a title string or a dict containing ``title`` and ``description``.
        Returns:
            URL of the generated image, or a deterministic placeholder.
        """
        # Normalise input
        if isinstance(event, dict):
            title = event.get("title", "Event")
            desc = event.get("description", "")
        else:
            title = str(event)
            desc = ""
        if not self.client or not self.settings.OPENAI_API_KEY or self.settings.OPENAI_API_KEY == "dummy-openai-key":
            slug = "-".join(title.lower().split()) or "event"
            return f"https://placehold.co/1024x512?text={slug}"

        prompt = f"Create a vivid banner image for an event titled '{title}'. {desc}"
        try:
            response = self.client.images.generate(
                prompt=prompt,
                n=1,
                size="1024x512",
            )
            url = response.data[0].url or ""
            self.logger.debug("Generated image URL via OpenAI: %s", url)
            return url or f"https://placehold.co/1024x512?text={'-'.join(title.lower().split()) or 'event'}"
        except Exception as exc:  # pragma: no cover - networked provider errors are environment-specific
            self.logger.warning("OpenAI image generation failed, using fallback: %s", exc)
            slug = "-".join(title.lower().split()) or "event"
            return f"https://placehold.co/1024x512?text={slug}"
