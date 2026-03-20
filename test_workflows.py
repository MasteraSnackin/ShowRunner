import json

from app.agent.orchestrator import handle_event
from app.agent.tools import get_endless_client, get_state_store


def test_create_event_parses_quoted_arguments():
    channel_id = "C-quoted-args"

    handle_event(
        {
            "type": "command",
            "channel_id": channel_id,
            "user_id": "U-quoted-args",
            "text": '/create_event title="Launch Party" description="VIP night"',
        }
    )

    state = get_state_store().get_latest_event_by_channel(channel_id)
    assert state is not None
    assert state.title == "Launch Party"
    assert state.description.startswith("Launch Party:")
    assert "VIP night" in state.description


def test_settlement_and_payout_use_latest_matching_state():
    channel_id = "C-duplicate-onchain"
    store = get_state_store()
    endless = get_endless_client()

    handle_event(
        {
            "type": "command",
            "channel_id": channel_id,
            "user_id": "U-duplicate-onchain-1",
            "text": '/create_event title="First Event" description="One"',
        }
    )
    first_state = store.get_latest_event_by_channel(channel_id)
    assert first_state is not None

    handle_event(
        {
            "type": "command",
            "channel_id": channel_id,
            "user_id": "U-duplicate-onchain-2",
            "text": '/create_event title="Second Event" description="Two"',
        }
    )
    latest_state = store.get_latest_event_by_channel(channel_id)
    assert latest_state is not None

    # Simulate a process restart resetting the stubbed remote ID sequence.
    latest_state.onchain_event_id = first_state.onchain_event_id
    latest_state = store.update_state(latest_state)

    endless.record_sale(int(latest_state.onchain_event_id), "buyer-1", 2)

    handle_event(
        {
            "type": "button_click",
            "channel_id": channel_id,
            "user_id": "U-duplicate-onchain-2",
            "button_id": "event:settle:duplicate",
            "payload": json.dumps(
                {"action": "settle", "event_id": latest_state.onchain_event_id}
            ),
        }
    )
    handle_event(
        {
            "type": "button_click",
            "channel_id": channel_id,
            "user_id": "U-duplicate-onchain-2",
            "button_id": "event:approve_payout:duplicate",
            "payload": json.dumps(
                {
                    "action": "approve_payout",
                    "event_id": latest_state.onchain_event_id,
                }
            ),
        }
    )

    refreshed_state = store.get_event_by_id(latest_state.id)
    assert refreshed_state is not None
    assert refreshed_state.title == "Second Event"
    assert refreshed_state.status == "settled"
