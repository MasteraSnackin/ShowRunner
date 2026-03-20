'''Civic data models.

These models represent the minimal set of structures required for the guardrail
service. In a production system they would be richer and likely generated from
OpenAPI specifications.
''' 

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ToolIntention:
    """A request to use a particular tool.

    * ``tool_name`` – the identifier of the tool (e.g. ``"send_message"``).
    * ``args`` – a mapping of argument names to values that would be passed to
      the tool.
    """

    tool_name: str
    args: Dict[str, Any]


@dataclass
class CivicDecision:
    """Result of a guardrail evaluation.

    * ``allowed`` – ``True`` if the tool usage is permitted.
    * ``reason`` – Human‑readable explanation for the decision.
    """

    allowed: bool
    reason: str
