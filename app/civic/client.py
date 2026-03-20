'''Civic client stub.

The client evaluates a ``ToolIntention`` against the configured guardrail
policies. In this prototype we only have a permissive ``allow_all`` policy, so
the client simply forwards the intention to that function.
''' 

from __future__ import annotations

from .models import ToolIntention, CivicDecision
from .policies import allow_all


class CivicClient:
    """Simple client that checks tool usage against guardrail policies.

    In a full implementation this would likely make HTTP calls to a remote
    policy service. Here we keep everything in‑process for speed and testability.
    """

    def __init__(self):
        # No configuration needed for the stub
        pass

    def evaluate_intention(self, intention: ToolIntention) -> CivicDecision:
        """Return a ``CivicDecision`` for *intention*.

        Currently this always calls :func:`allow_all` which permits the request.
        """
        return allow_all(intention)
