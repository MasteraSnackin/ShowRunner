'''Agent workflow implementations.

The workflows orchestrate interactions between the various stub services:

* ``LuffaClient`` – sends messages back to the chat platform.
* ``LLMClient`` – generates descriptions and images for events.
* ``EndlessClient`` – creates ticket types and calculates sales.
* ``CivicClient`` – evaluates whether a tool usage is allowed.
* ``StateStore`` – persists the ``EventState`` for each event.

Each workflow receives a concrete event dataclass from ``app.luffa.webhooks`` and
returns ``None``; side‑effects (sending messages, persisting state) are performed
inside the function.
''' 

from __future__ import annotations

import shlex
from typing import Any

from ..luffa.webhooks import (
    MessageCommandEvent,
    ButtonClickEvent,
    LuffaEvent,
)
from ..state_store import EventState
from .tools import (
    get_logger_instance,
    get_state_store,
    get_luffa_client,
    get_llm_client,
    get_endless_client,
    get_civic_client,
)

_logger = get_logger_instance()
_state_store = get_state_store()
_luffa = get_luffa_client()
_llm = get_llm_client()
_endless = get_endless_client()
_civic = get_civic_client()


def _ensure_allowed(tool_name: str, args: dict[str, Any]) -> bool:
    """Ask the ``CivicClient`` whether a tool usage is permitted.

    Returns ``True`` if allowed, otherwise logs a warning and returns ``False``.
    """
    intention = {
        "tool_name": tool_name,
        "args": args,
    }
    # The stub client expects a ``ToolIntention`` dataclass; we construct it
    from ..civic.models import ToolIntention

    decision = _civic.evaluate_intention(ToolIntention(tool_name=tool_name, args=args))
    if not decision.allowed:
        _logger.warning("Civic denied tool %s: %s", tool_name, decision.reason)
    return decision.allowed


def start_event_creation(event: MessageCommandEvent) -> None:
    """Handle a ``/create_event`` command from Luffa.

    Expected command format (simplified)::

        /create_event title="My Event" description="Short desc"

    The workflow:

    1. Parse arguments (title, description) from ``event.command``.
    2. Ask Civic if we may call the LLM and Endless services.
    3. Use ``LLMClient`` to generate a longer description and an image URL.
    4. Create a ticket type via ``EndlessClient``.
    5. Persist the new ``EventState``.
    6. Send a confirmation message back to the channel.
    """
    if not _ensure_allowed("start_event_creation", {"event": event}):
        return

    # Preserve quoted values such as title="Launch Party".
    args: dict[str, str] = {}
    for part in shlex.split(event.text)[1:]:  # skip the command name
        if "=" in part:
            key, val = part.split("=", 1)
            args[key] = val.strip('"')
    title = args.get("title", "Untitled Event")
    short_desc = args.get("description", "No description provided.")

    # Generate richer description and image via LLM stub
    description = _llm.generate_description(title, short_desc)
    image_url = _llm.generate_image_url({"title": title, "description": short_desc})

    # Create ticket type on Endless (stubbed)
    ticket = _endless.create_ticket_type(
        event_id=event.channel_id,  # using channel_id as a placeholder event identifier
        title=title,
        description=description,
        price=10.0,
        supply=100,
        image_url=image_url,
    )
    # ``ticket`` may be a dict with details or an int representing the onchain_event_id.
    if isinstance(ticket, dict):
        price = ticket.get("price", 10.0)
        supply = ticket.get("supply", 100)
        onchain_event_id = ticket.get("event_id", event.channel_id)
    else:
        # Assume ticket is the onchain_event_id (int)
        price = 10.0
        supply = 100
        onchain_event_id = ticket

    # Persist state
    state = EventState(
        channel_id=event.channel_id,
        status="open",
        title=title,
        description=description,
        banner_url=image_url,
        price=price,
        supply=supply,
        onchain_event_id=onchain_event_id,
    )
    _state_store.create_state(state)

    # Send confirmation back to Luffa
    confirmation = (
        f"Event *{title}* created!\n"
        f"Description: {description}\n"
        f"Ticket price: ${state.price:.2f}, supply: {state.supply}\n"
        f"Image: {state.banner_url}"
    )
    _luffa.send_message(event.channel_id, confirmation)


def start_settlement(event: ButtonClickEvent) -> None:
    """Handle a "settle" button click.

    The button payload is expected to contain ``event_id`` identifying the
    ``EventState``. The workflow:

    1. Load the ``EventState``.
    2. Ask Civic if settlement is allowed.
    3. Use ``EndlessClient`` to compute a sales summary.
    4. Generate a summary message via ``LLMClient``.
    5. Send the summary back to the channel.
    """
    if not _ensure_allowed("start_settlement", {"event": event}):
        return

    # ``event.payload`` is a JSON string – we expect it to contain ``event_id``
    import json

    try:
        payload = json.loads(event.payload)
        event_id = payload.get("event_id")
        state_id = payload.get("state_id")
    except Exception as exc:
        _logger.error("Failed to parse settlement payload: %s", exc)
        return

    state = None
    if state_id is not None:
        state = _state_store.get_event_by_id(int(state_id))
    if not state and event_id is not None:
        state = _state_store.get_state(event_id)
    if not state:
        _logger.error("No state found for event_id %s", event_id)
        return

    summary = _endless.sales_summary(event_id)
    # Use LLM to turn the raw numbers into a friendly message
    friendly = _llm.generate_description(
        f"Settlement for {state.title}",
        f"Tickets sold: {summary['tickets_sold']}, revenue: ${summary['revenue']:.2f}",
    )

    message = (
        f"*Settlement Report for {state.title}*\n"
        f"{friendly}\n"
        f"Tickets sold: {summary['tickets_sold']}\n"
        f"Revenue: ${summary['revenue']:.2f}\n"
        f"Payout amount: ${summary['payout_amount']:.2f}"
    )
    state.status = "ready_for_payout"
    _state_store.update_state(state)
    _luffa.send_message(event.channel_id, message)


def approve_payout(event: ButtonClickEvent) -> None:
    """Handle a "approve payout" button click.

    The payload must contain ``event_id``. The workflow:

    1. Load the ``EventState``.
    2. Ask Civic if payout is allowed.
    3. Call ``EndlessClient.approve_payout``.
    4. Notify the channel.
    """
    if not _ensure_allowed("approve_payout", {"event": event}):
        return

    import json

    try:
        payload = json.loads(event.payload)
        event_id = payload.get("event_id")
        state_id = payload.get("state_id")
    except Exception as exc:
        _logger.error("Failed to parse payout payload: %s", exc)
        return

    state = None
    if state_id is not None:
        state = _state_store.get_event_by_id(int(state_id))
    if not state and event_id is not None:
        state = _state_store.get_state(event_id)
    if not state:
        _logger.error("No state found for event_id %s", event_id)
        return

    _endless.approve_payout(state.onchain_event_id or event_id)
    state.status = "settled"
    _state_store.update_state(state)
    _luffa.send_message(event.channel_id, f"Payout approved for event *{state.title}*.")
