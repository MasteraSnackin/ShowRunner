'''LLM client stub.

In the real system this would call an LLM service (e.g. OpenAI) to generate a
human‑readable description of an event and optionally an image URL. For the
purposes of the hackathon we provide deterministic placeholder implementations
so that the rest of the code can be exercised without external dependencies.
''' 

from __future__ import annotations

from typing import Dict

from ..config import Settings
from ..logging_config import get_logger


class LLMClient:
    """Very small wrapper that pretends to talk to an LLM.

    The methods return static strings that are sufficient for the downstream
    workflow logic. They accept the same arguments that a real implementation
    would need, making it easy to replace this stub with a proper LLM client
    later.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)

    def generate_description(self, event: Dict) -> str:
        """Return a placeholder description for *event*.

        ``event`` is expected to be a mapping containing at least ``title`` and
        ``price`` keys. The stub simply formats those values into a sentence.
        """
        title = event.get("title", "Untitled Event")
        price = event.get("price", 0)
        description = f"{title} – a fantastic experience priced at {price} ETH."
        self.logger.debug("Generated description: %s", description)
        return description

    def generate_image_url(self, event: Dict) -> str:
        """Return a deterministic placeholder image URL.

        In a production system this would call an image generation model. Here we
        return a static URL that points to a generic placeholder image.
        """
        placeholder = "https://via.placeholder.com/800x400.png?text=Event+Banner"
        self.logger.debug("Generated image URL: %s", placeholder)
        return placeholder
