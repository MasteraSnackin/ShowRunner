from __future__ import annotations

import asyncio
import json

from app.main import app


async def asgi_request(
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes = b"",
) -> tuple[int, dict[str, str], bytes]:
    response_status = 500
    response_headers: dict[str, str] = {}
    body_parts: list[bytes] = []
    request_complete = False

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "headers": [
            (key.lower().encode("latin-1"), value.encode("latin-1"))
            for key, value in (headers or {}).items()
        ],
        "client": ("testclient", 123),
        "server": ("testserver", 80),
    }

    async def receive() -> dict[str, object]:
        nonlocal request_complete
        if request_complete:
            return {"type": "http.disconnect"}
        request_complete = True
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message: dict[str, object]) -> None:
        nonlocal response_status, response_headers
        if message["type"] == "http.response.start":
            response_status = int(message["status"])
            response_headers = {
                key.decode("latin-1"): value.decode("latin-1")
                for key, value in message["headers"]
            }
        elif message["type"] == "http.response.body":
            body_parts.append(message.get("body", b""))

    await app(scope, receive, send)
    return response_status, response_headers, b"".join(body_parts)


def test_health_route_returns_json():
    status, headers, body = asyncio.run(asgi_request("GET", "/api/health"))

    assert status == 200
    assert headers["content-type"].startswith("application/json")
    assert json.loads(body) == {"message": "ShowRunner API is running"}


def test_dashboard_root_serves_html_for_browser_requests():
    status, headers, body = asyncio.run(
        asgi_request("GET", "/", headers={"accept": "text/html"})
    )

    assert status == 200
    assert headers["content-type"].startswith("text/html")
    assert b"Encode ShowRunner Dashboard" in body


def test_head_root_returns_ok_without_body():
    status, headers, body = asyncio.run(asgi_request("HEAD", "/"))

    assert status == 200
    assert body == b""
    assert "content-type" not in headers or headers["content-type"] in {
        "",
        "application/json",
    }


def test_demo_api_flow_via_http_routes():
    create_payload = json.dumps(
        {
            "title": "Route Test Event",
            "description": "Exercise the dashboard endpoints end to end.",
            "channel_id": "route-http-flow",
        }
    ).encode()

    status, _, body = asyncio.run(
        asgi_request(
            "POST",
            "/api/demo/events",
            headers={"content-type": "application/json"},
            body=create_payload,
        )
    )
    created = json.loads(body)

    assert status == 200
    assert created["title"] == "Route Test Event"
    assert created["status"] == "open"

    sale_payload = json.dumps({"quantity": 2}).encode()
    status, _, _ = asyncio.run(
        asgi_request(
            "POST",
            f"/api/demo/events/{created['id']}/sales",
            headers={"content-type": "application/json"},
            body=sale_payload,
        )
    )
    assert status == 200

    status, _, body = asyncio.run(
        asgi_request("POST", f"/api/demo/events/{created['id']}/settle")
    )
    settled = json.loads(body)
    assert status == 200
    assert settled["status"] == "ready_for_payout"

    status, _, body = asyncio.run(
        asgi_request("POST", f"/api/demo/events/{created['id']}/payout")
    )
    paid = json.loads(body)
    assert status == 200
    assert paid["status"] == "settled"

    status, _, body = asyncio.run(asgi_request("GET", "/api/events"))
    payload = json.loads(body)
    matching = next(event for event in payload["events"] if event["id"] == created["id"])
    assert matching["status"] == "settled"

    status, _, body = asyncio.run(
        asgi_request("GET", f"/api/events/{created['id']}")
    )
    event_detail = json.loads(body)
    assert status == 200
    assert event_detail["id"] == created["id"]
    assert event_detail["status"] == "settled"

    status, _, body = asyncio.run(
        asgi_request("GET", f"/api/events/{created['id']}/sales-summary")
    )
    sales_summary = json.loads(body)
    assert status == 200
    assert sales_summary["event_id"] == created["id"]
    assert sales_summary["tickets_sold"] == 2
    assert sales_summary["revenue"] == 20.0


def test_webhook_rejects_invalid_json_with_structured_400():
    status, headers, body = asyncio.run(
        asgi_request(
            "POST",
            "/webhook",
            headers={"content-type": "application/json"},
            body=b"{bad json",
        )
    )

    payload = json.loads(body)
    assert status == 400
    assert headers["content-type"].startswith("application/json")
    assert payload["error"]["code"] == "bad_request"
    assert payload["error"]["message"] == "Webhook payload must be valid JSON"


def test_payout_rejects_invalid_transition_with_conflict():
    create_payload = json.dumps(
        {
            "title": "Transition Guard Event",
            "description": "Used to verify payout validation.",
            "channel_id": "route-invalid-transition",
        }
    ).encode()

    status, _, body = asyncio.run(
        asgi_request(
            "POST",
            "/api/demo/events",
            headers={"content-type": "application/json"},
            body=create_payload,
        )
    )
    created = json.loads(body)
    assert status == 200

    status, headers, body = asyncio.run(
        asgi_request("POST", f"/api/demo/events/{created['id']}/payout")
    )
    payload = json.loads(body)
    assert status == 409
    assert headers["content-type"].startswith("application/json")
    assert payload["error"]["code"] == "conflict"
    assert payload["error"]["details"]["status"] == "open"


def test_sales_reject_after_event_is_settled():
    create_payload = json.dumps(
        {
            "title": "Settled Guard Event",
            "description": "Used to verify sales validation after settlement.",
            "channel_id": "route-sales-after-settled",
        }
    ).encode()

    status, _, body = asyncio.run(
        asgi_request(
            "POST",
            "/api/demo/events",
            headers={"content-type": "application/json"},
            body=create_payload,
        )
    )
    created = json.loads(body)
    assert status == 200

    sale_payload = json.dumps({"quantity": 1}).encode()
    status, _, _ = asyncio.run(
        asgi_request(
            "POST",
            f"/api/demo/events/{created['id']}/sales",
            headers={"content-type": "application/json"},
            body=sale_payload,
        )
    )
    assert status == 200

    status, _, _ = asyncio.run(
        asgi_request("POST", f"/api/demo/events/{created['id']}/settle")
    )
    assert status == 200

    status, _, body = asyncio.run(
        asgi_request(
            "POST",
            f"/api/demo/events/{created['id']}/sales",
            headers={"content-type": "application/json"},
            body=sale_payload,
        )
    )
    payload = json.loads(body)
    assert status == 409
    assert payload["error"]["code"] == "conflict"
    assert payload["error"]["details"]["status"] == "ready_for_payout"


def test_demo_reset_clears_persisted_events():
    create_payload = json.dumps(
        {
            "title": "Reset Candidate",
            "description": "Used to verify demo reset behavior.",
            "channel_id": "route-reset-flow",
        }
    ).encode()

    status, _, body = asyncio.run(
        asgi_request(
            "POST",
            "/api/demo/events",
            headers={"content-type": "application/json"},
            body=create_payload,
        )
    )
    assert status == 200
    created = json.loads(body)

    status, _, body = asyncio.run(asgi_request("POST", "/api/demo/reset"))
    payload = json.loads(body)
    assert status == 200
    assert payload["status"] == "reset"
    assert payload["deleted_events"] >= 1

    status, _, body = asyncio.run(asgi_request("GET", "/api/events"))
    listing = json.loads(body)
    assert listing["counts"]["total"] == 0

    status, _, body = asyncio.run(
        asgi_request("GET", f"/api/events/{created['id']}")
    )
    missing = json.loads(body)
    assert status == 404
    assert missing["error"]["code"] == "not_found"
