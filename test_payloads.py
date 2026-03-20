import json
import pytest
from app.agent.orchestrator import handle_event

@pytest.fixture
def sample_payloads():
    command = {
        "type": "command",
        "channel_id": "C123",
        "user_id": "U456",
        "text": "/create_event",
    }
    settlement = {
        "type": "button_click",
        "channel_id": "C123",
        "user_id": "U456",
        "button_id": "event:settle:1",
        "payload": json.dumps({"action": "settle"}),
    }
    payout = {
        "type": "button_click",
        "channel_id": "C123",
        "user_id": "U456",
        "button_id": "event:approve_payout:1",
        "payload": json.dumps({"action": "approve_payout"}),
    }
    return command, settlement, payout

def test_command_payload(caplog, sample_payloads):
    command, _, _ = sample_payloads
    with caplog.at_level("INFO"):
        handle_event(command)
    assert "Routing to start_event_creation" in caplog.text

def test_settlement_payload(caplog, sample_payloads):
    _, settlement, _ = sample_payloads
    with caplog.at_level("INFO"):
        handle_event(settlement)
    assert "Routing to start_settlement" in caplog.text

def test_payout_payload(caplog, sample_payloads):
    _, _, payout = sample_payloads
    with caplog.at_level("INFO"):
        handle_event(payout)
    assert "Routing to approve_payout" in caplog.text
