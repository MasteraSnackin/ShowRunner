'''Civic guardrail policies.

For this prototype we implement a single permissive policy that always
allows the requested tool usage. In a real deployment policies would inspect
the ``ToolIntention`` and enforce business rules, rate limits, content
moderation, etc.
''' 

from __future__ import annotations

from .models import ToolIntention, CivicDecision


def allow_all(intention: ToolIntention) -> CivicDecision:
    """Unconditionally allow any tool intention.

    Returns a ``CivicDecision`` with ``allowed=True`` and a generic reason.
    """
    return CivicDecision(allowed=True, reason="All tool usages are permitted in the stub implementation.")
