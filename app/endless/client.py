'''Endless HTTP client stub.

The real Endless service provides on‑chain ticket creation, sales tracking and
payout execution. For this hackathon we implement an in‑memory stub that mimics
the essential behaviour required by the orchestrator.
''' 

from __future__ import annotations

import itertools
from dataclasses import dataclass, asdict
from typing import Dict, List, Any

from ..config import Settings
from ..logging_config import get_logger


@dataclass
class TicketType:
    ticket_type_id: int
    event_id: int | str
    title: str
    price: float
    supply: int
    description: str
    image_url: str


class EndlessClient:
    """In‑memory stub for the Endless ticketing service.

    It stores ticket types and simulated sales data in dictionaries. All data is
    lost when the process restarts – which is acceptable for a prototype.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(self.__class__.__name__)
        # Auto‑incrementing IDs for ticket types
        self._ticket_type_counter = itertools.count(1)
        # ticket_type_id -> TicketType
        self._ticket_types: Dict[int, TicketType] = {}
        # event_id -> list of sales (each sale is a dict with buyer, quantity)
        self._sales: Dict[int, List[Dict[str, Any]]] = {}
        # Simple counter for transaction hashes
        self._tx_counter = itertools.count(1)

    # ---------------------------------------------------------------------
    # Ticket type management
    # ---------------------------------------------------------------------
    def create_ticket_type(
        self,
        event_id: int,
        title: str,
        price: float,
        supply: int,
        description: str,
        image_url: str,
    ) -> int:
        """Create a ticket type for *event_id* and return its ID.

        The stub does not enforce supply limits – it merely records the
        definition.
        """
        ticket_type_id = next(self._ticket_type_counter)
        ticket = TicketType(
            ticket_type_id=ticket_type_id,
            event_id=event_id,
            title=title,
            price=price,
            supply=supply,
            description=description,
            image_url=image_url,
        )
        self._ticket_types[ticket_type_id] = ticket
        self.logger.debug("Created ticket type %s", asdict(ticket))
        return ticket_type_id

    # ---------------------------------------------------------------------
    # Sales summary
    # ---------------------------------------------------------------------
    def record_sale(self, event_id: int, buyer: str, quantity: int) -> None:
        """Record a simulated sale – used by tests or manual interaction.
        """
        self._sales.setdefault(event_id, []).append({"buyer": buyer, "quantity": quantity})
        self.logger.debug("Recorded sale for event %s: %s x %s", event_id, quantity, buyer)

    def get_sales_summary(self, event_id: int) -> Dict[str, Any]:
        """Return a summary of sales for *event_id*.

        The returned dict contains ``total_sales`` (number of tickets sold),
        ``total_revenue`` (price * quantity) and a ``sales`` list with the raw
        sale records.
        """
        sales = self._sales.get(event_id, [])
        total_sales = sum(s["quantity"] for s in sales)
        # Calculate revenue using ticket price if a ticket type exists
        ticket_price = 0.0
        ticket = self._ticket_types.get(int(event_id))
        if ticket is not None:
            ticket_price = ticket.price
        else:
            for ticket in self._ticket_types.values():
                if str(ticket.event_id) == str(event_id):
                    ticket_price = ticket.price
                    break
        total_revenue = total_sales * ticket_price
        summary = {
            "total_sales": total_sales,
            "total_revenue": total_revenue,
            "sales": sales,
        }
        self.logger.debug("Sales summary for event %s: %s", event_id, summary)
        return summary

    def sales_summary(self, event_id: int | str) -> Dict[str, Any]:
        """Compatibility wrapper for workflow code expecting friendlier keys."""
        summary = self.get_sales_summary(int(event_id))
        total_revenue = float(summary["total_revenue"])
        payout_amount = total_revenue * 0.9
        return {
            "tickets_sold": summary["total_sales"],
            "revenue": total_revenue,
            "payout_amount": payout_amount,
            "sales": summary["sales"],
        }

    # ---------------------------------------------------------------------
    # Payout execution
    # ---------------------------------------------------------------------
    def execute_payouts(self, event_id: int) -> Dict[str, str]:
        """Simulate payout execution and return a transaction hash.
        """
        tx_hash = f"0xdeadbeef{next(self._tx_counter):06x}"
        self.logger.info("Executed payout for event %s, tx %s", event_id, tx_hash)
        return {"transaction_hash": tx_hash}

    def approve_payout(self, event_id: int | str) -> Dict[str, str]:
        """Compatibility wrapper for workflow code."""
        return self.execute_payouts(int(event_id))

    def reset_demo_state(self) -> None:
        """Clear in-memory stub state for tests and demo resets."""
        self._ticket_type_counter = itertools.count(1)
        self._ticket_types.clear()
        self._sales.clear()
        self._tx_counter = itertools.count(1)
        self.logger.info("Reset Endless demo state")
