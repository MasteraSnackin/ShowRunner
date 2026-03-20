from __future__ import annotations

from sqlalchemy import inspect

from app.agent.tools import get_state_store


def test_state_store_declares_lookup_indexes():
    inspector = inspect(get_state_store().engine)
    index_names = {index["name"] for index in inspector.get_indexes("events")}

    assert "ix_events_channel_id_id" in index_names
    assert "ix_events_channel_status_id" in index_names
    assert "ix_events_onchain_event_id_id" in index_names
    assert "ix_events_status" in index_names
