from app.main import (
    CreateEventRequest,
    RecordSaleRequest,
    approve_demo_payout,
    build_dashboard_payload,
    create_demo_event,
    record_demo_sale,
    settle_demo_event,
)


def test_dashboard_flow_updates_counts_and_statuses():
    created = create_demo_event(
        CreateEventRequest(
            title="Investor Breakfast",
            description="Private founder updates before doors open.",
            channel_id="dashboard-flow",
        )
    )

    record_demo_sale(created["id"], RecordSaleRequest(quantity=3))
    settled = settle_demo_event(created["id"])
    paid = approve_demo_payout(created["id"])
    payload = build_dashboard_payload()

    assert created["status"] == "open"
    assert settled["status"] == "ready_for_payout"
    assert paid["status"] == "settled"
    assert payload["counts"]["settled"] >= 1


def test_dashboard_payload_exposes_action_flags():
    created = create_demo_event(
        CreateEventRequest(
            title="Builder Session",
            description="Hands-on demo rehearsal and technical QA.",
            channel_id="dashboard-actions",
        )
    )

    payload = build_dashboard_payload()
    matching = next(event for event in payload["events"] if event["id"] == created["id"])

    assert matching["actions"]["can_record_sale"] is True
    assert matching["actions"]["can_settle"] is True
    assert matching["actions"]["can_payout"] is False


def test_dashboard_create_preserves_embedded_quotes():
    created = create_demo_event(
        CreateEventRequest(
            title='Founder "Town Hall"',
            description='Quoted "VIP" seating for launch night.',
            channel_id="dashboard-quoted-fields",
        )
    )

    assert created["title"] == 'Founder "Town Hall"'
    assert created["description"].startswith('Founder "Town Hall":')
    assert '"VIP"' in created["description"]
