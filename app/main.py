"""FastAPI entrypoint for the root ShowRunner application package."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .agent.orchestrator import handle_event
from .agent.tools import get_endless_client, get_state_store
from .state_store import EventState

app = FastAPI(title="Encode ShowRunner")

STATIC_DIR = Path(__file__).with_name("static")
INDEX_FILE = STATIC_DIR / "index.html"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class CreateEventRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=80)
    description: str = Field(..., min_length=4, max_length=180)
    channel_id: str = Field(default="demo-room", min_length=2, max_length=40)


class RecordSaleRequest(BaseModel):
    quantity: int = Field(default=1, ge=1, le=25)


def serialize_event(state: EventState) -> dict[str, object]:
    return {
        "id": state.id,
        "channel_id": state.channel_id,
        "title": state.title,
        "description": state.description,
        "status": state.status,
        "banner_url": state.banner_url,
        "price": state.price,
        "supply": state.supply,
        "onchain_event_id": state.onchain_event_id,
        "actions": {
            "can_record_sale": state.status in {"open", "ready_for_payout"},
            "can_settle": state.status == "open",
            "can_payout": state.status == "ready_for_payout",
        },
    }


def build_dashboard_payload() -> dict[str, object]:
    store = get_state_store()
    events = [serialize_event(event) for event in store.list_events()]
    counts = {
        "total": len(events),
        "open": sum(1 for event in events if event["status"] == "open"),
        "ready_for_payout": sum(1 for event in events if event["status"] == "ready_for_payout"),
        "settled": sum(1 for event in events if event["status"] == "settled"),
    }
    return {"events": events, "counts": counts}


def require_event(state_id: int) -> EventState:
    state = get_state_store().get_event_by_id(state_id)
    if not state:
        raise HTTPException(status_code=404, detail=f"Event {state_id} not found")
    return state


def create_demo_event(data: CreateEventRequest) -> dict[str, object]:
    handle_event(
        {
            "type": "command",
            "channel_id": data.channel_id,
            "user_id": "dashboard-user",
            "text": (
                f"/create_event "
                f"title={json.dumps(data.title)} "
                f"description={json.dumps(data.description)}"
            ),
        }
    )
    state = get_state_store().get_latest_event_by_channel(data.channel_id)
    if not state:
        raise HTTPException(status_code=500, detail="Event was not persisted")
    return serialize_event(state)


def record_demo_sale(state_id: int, data: RecordSaleRequest) -> dict[str, object]:
    state = require_event(state_id)
    if not state.onchain_event_id:
        raise HTTPException(status_code=409, detail="Event is missing an on-chain identifier")
    get_endless_client().record_sale(int(state.onchain_event_id), "dashboard-buyer", data.quantity)
    return serialize_event(state)


def settle_demo_event(state_id: int) -> dict[str, object]:
    state = require_event(state_id)
    if not state.onchain_event_id:
        raise HTTPException(status_code=409, detail="Event is missing an on-chain identifier")
    handle_event(
        {
            "type": "button_click",
            "channel_id": state.channel_id,
            "user_id": "dashboard-user",
            "button_id": f"event:settle:{state.id}",
            "payload": json.dumps(
                {
                    "action": "settle",
                    "event_id": state.onchain_event_id,
                    "state_id": state.id,
                }
            ),
        }
    )
    refreshed = require_event(state_id)
    return serialize_event(refreshed)


def approve_demo_payout(state_id: int) -> dict[str, object]:
    state = require_event(state_id)
    if not state.onchain_event_id:
        raise HTTPException(status_code=409, detail="Event is missing an on-chain identifier")
    handle_event(
        {
            "type": "button_click",
            "channel_id": state.channel_id,
            "user_id": "dashboard-user",
            "button_id": f"event:approve_payout:{state.id}",
            "payload": json.dumps(
                {
                    "action": "approve_payout",
                    "event_id": state.onchain_event_id,
                    "state_id": state.id,
                }
            ),
        }
    )
    refreshed = require_event(state_id)
    return serialize_event(refreshed)


@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return FileResponse(INDEX_FILE)
    return JSONResponse({"message": "ShowRunner API is running"})


@app.get("/dashboard")
async def dashboard() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"message": "ShowRunner API is running"}


@app.get("/api/events")
async def list_events() -> dict[str, object]:
    return build_dashboard_payload()


@app.post("/api/demo/events")
async def post_event(data: CreateEventRequest) -> dict[str, object]:
    return create_demo_event(data)


@app.post("/api/demo/events/{state_id}/sales")
async def post_sale(state_id: int, data: RecordSaleRequest) -> dict[str, object]:
    return record_demo_sale(state_id, data)


@app.post("/api/demo/events/{state_id}/settle")
async def post_settle(state_id: int) -> dict[str, object]:
    return settle_demo_event(state_id)


@app.post("/api/demo/events/{state_id}/payout")
async def post_payout(state_id: int) -> dict[str, object]:
    return approve_demo_payout(state_id)


@app.post("/webhook")
async def webhook(request: Request) -> dict[str, str]:
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Webhook payload must be a JSON object")
    handle_event(payload)
    return {"status": "accepted"}
