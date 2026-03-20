'''Orchestrator for routing incoming Luffa webhook events to the appropriate workflow.

The orchestrator is deliberately lightweight – it parses the raw payload using
`app.luffa.webhooks.parse_incoming` and then dispatches to one of the three
workflow functions defined in `app.agent.workflows`.

All side‑effects (sending messages, persisting state, etc.) are handled inside
the workflow implementations.
''' 

from __future__ import annotations

import json

from ..luffa.webhooks import (
    LuffaEvent,
    MessageCommandEvent,
    ButtonClickEvent,
    parse_incoming,
)
from ..logging_config import get_logger
from .workflows import start_event_creation, start_settlement, approve_payout

_logger = get_logger(__name__)


def handle_event(payload: dict) -> None:
    """Parse a raw webhook payload and invoke the matching workflow.

    The function is tolerant of unexpected payloads – any parsing error is logged
    and the request is ignored.
    """
    try:
        event: LuffaEvent = parse_incoming(payload)
    except Exception as exc:
        _logger.error("Failed to parse incoming webhook: %s", exc)
        return

    # Command‑type events – currently only the `/create_event` command.
    if isinstance(event, MessageCommandEvent):
        if event.command.startswith("/create_event"):
            _logger.info("Routing to start_event_creation for channel %s", event.channel_id)
            start_event_creation(event)
        else:
            _logger.warning("Unrecognised command: %s", event.command)
        return

    # Button click events – the payload is expected to be a JSON string with an
    # ``action`` field that tells us which workflow to run.
    if isinstance(event, ButtonClickEvent):
        try:
            data = json.loads(event.payload)
            action = data.get("action")
        except Exception as exc:
            _logger.error("Failed to decode button payload: %s", exc)
            return

        if action == "settle":
            _logger.info("Routing to start_settlement for channel %s", event.channel_id)
            start_settlement(event)
        elif action == "approve_payout":
            _logger.info("Routing to approve_payout for channel %s", event.channel_id)
            approve_payout(event)
        else:
            _logger.warning("Unknown button action: %s", action)
        return

    _logger.warning("Received unsupported Luffa event type: %s", type(event))
