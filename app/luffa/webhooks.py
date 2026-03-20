'''Luffa webhook parsing.

Defines dataclasses representing the two webhook event types we care about:
* ``MessageCommandEvent`` – a slash‑command message (e.g. ``/event new``)
* ``ButtonClickEvent`` – a button click on a card posted by the bot

The ``parse_incoming`` function receives the raw JSON payload from Luffa and
returns an instance of one of the above classes (or ``None`` if the payload
does not match the expected shape).
''' 

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional, Dict, Any


# ---------------------------------------------------------------------------
# Event dataclasses
# ---------------------------------------------------------------------------
@dataclass
class LuffaEvent:
    channel_id: str
    user_id: str
    raw: Dict[str, Any]


@dataclass
class MessageCommandEvent(LuffaEvent):
    command: str  # e.g. "/event new"
    text: str


@dataclass
class ButtonClickEvent(LuffaEvent):
    button_id: str  # e.g. "event:approve_payout:1"
    payload: str  # JSON string payload from the button click


# ---------------------------------------------------------------------------
# Helper to safely extract values from the payload
# ---------------------------------------------------------------------------
def _get_str(payload: Dict[str, Any], *keys: str) -> Optional[str]:
    """Navigate ``payload`` using ``keys`` and return the value if it is a string.
    Returns ``None`` if any key is missing or the final value is not a string.
    """
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current if isinstance(current, str) else None


def parse_incoming(body: str | bytes | Dict[str, Any]) -> Optional[LuffaEvent]:
    """Parse a Luffa webhook payload.

    The function accepts either a raw JSON string, ``bytes`` or an already
    parsed ``dict``. It returns a concrete ``LuffaEvent`` subclass instance or
    ``None`` when the payload does not represent a supported event.
    """
    if isinstance(body, (str, bytes)):
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return None
    else:
        payload = body

    # Common fields
    channel_id = _get_str(payload, "channel_id")
    user_id = _get_str(payload, "user_id")
    if not channel_id or not user_id:
        return None

    event_type = _get_str(payload, "type")
    if event_type == "command":
        # Expected shape for a slash‑command
        text = _get_str(payload, "text")
        if not text:
            return None
        return MessageCommandEvent(
            channel_id=channel_id,
            user_id=user_id,
            raw=payload,
            command=text.split()[0] if text else "",
            text=text,
        )
    elif event_type == "button_click":
        button_id = _get_str(payload, "button_id")
        payload_str = _get_str(payload, "payload")
        if not button_id:
            return None
        return ButtonClickEvent(
            channel_id=channel_id,
            user_id=user_id,
            raw=payload,
            button_id=button_id,
            payload=payload_str or "{}",
        )
    # Unsupported event type
    return None
