'''State store module for Showrunner.

Provides a SQLAlchemy ORM model ``EventModel`` that mirrors the ``EventState``
Dataclass used throughout the application. ``StateStore`` wraps a SQLite
engine and offers simple CRUD helpers used by the orchestrator and
workflows.
'''

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional, List

from sqlalchemy import Column, Integer, String, Float, create_engine, select
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# ---------------------------------------------------------------------------
# ORM model definitions
# ---------------------------------------------------------------------------
Base = declarative_base()


class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    channel_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    banner_url = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    supply = Column(Integer, nullable=False)
    onchain_event_id = Column(String, nullable=True)

    def to_state(self) -> "EventState":
        return EventState(
            id=self.id,
            channel_id=self.channel_id,
            status=self.status,
            title=self.title,
            description=self.description,
            banner_url=self.banner_url,
            price=self.price,
            supply=self.supply,
            onchain_event_id=self.onchain_event_id,
        )


# ---------------------------------------------------------------------------
# Dataclass used by the rest of the code base
# ---------------------------------------------------------------------------
@dataclass
class EventState:
    channel_id: str
    status: str
    title: str
    description: str
    banner_url: str
    price: float
    supply: int
    id: Optional[int] = None
    onchain_event_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Store wrapper
# ---------------------------------------------------------------------------
class StateStore:
    """Simple wrapper around a SQLite database using SQLAlchemy.

    The class is deliberately lightweight – it creates a new ``Session`` for
    each operation and commits immediately. This is sufficient for the MVP
    and keeps the code easy to follow.
    """

    def __init__(self, db_url: str = "sqlite:///./showrunner.db") -> None:
        self.logger = logging.getLogger(__name__)
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        # Initialise session factory and create tables
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.logger.info("StateStore initialised with DB %s", db_url)

    def get_state(self, event_id: str) -> EventState | None:
        """Retrieve an ``EventState`` by its ``onchain_event_id``.

        Returns ``None`` if the state is not found.
        """
        with self._session() as session:
            result = session.execute(
                select(EventModel)
                .where(EventModel.onchain_event_id == str(event_id))
                .order_by(EventModel.id.desc())
            ).scalars().first()
            return result.to_state() if result else None

    # ---------------------------------------------------------------------
    # Helper to obtain a fresh session
    # ---------------------------------------------------------------------
    def _session(self) -> Session:
        return self.SessionLocal()

    # ---------------------------------------------------------------------
    # CRUD operations
    # ---------------------------------------------------------------------
    def create_event(self, state: EventState) -> EventState:
        """Persist a new ``EventState`` and return the stored instance.

        The ``id`` field is populated by the database and returned.
        """
        with self._session() as db:
            model = EventModel(
                channel_id=state.channel_id,
                status=state.status,
                title=state.title,
                description=state.description,
                banner_url=state.banner_url,
                price=state.price,
                supply=state.supply,
                onchain_event_id=state.onchain_event_id,
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            self.logger.debug("Created event %s", model.id)
            return model.to_state()

    # Compatibility alias for existing workflow code
    def create_state(self, state: EventState) -> EventState:
        """Alias for ``create_event`` to maintain backward compatibility.
        """
        return self.create_event(state)

    def get_event_by_id(self, event_id: int) -> Optional[EventState]:
        with self._session() as db:
            model = db.query(EventModel).filter(EventModel.id == event_id).first()
            return model.to_state() if model else None

    def get_latest_event_by_channel(
        self, channel_id: str, status: Optional[str] = None
    ) -> Optional[EventState]:
        """Return the most recent event for *channel_id* optionally filtered by *status*.
        """
        with self._session() as db:
            query = db.query(EventModel).filter(EventModel.channel_id == channel_id)
            if status:
                query = query.filter(EventModel.status == status)
            model = query.order_by(EventModel.id.desc()).first()
            return model.to_state() if model else None

    def list_events(self, limit: int = 24) -> List[EventState]:
        """Return recent events ordered newest-first."""
        with self._session() as db:
            models = db.query(EventModel).order_by(EventModel.id.desc()).limit(limit).all()
            return [model.to_state() for model in models]

    def update_event(self, state: EventState) -> EventState:
        """Update an existing event identified by ``state.id``.
        """
        if state.id is None:
            raise ValueError("EventState.id must be set for update")
        with self._session() as db:
            model = db.query(EventModel).filter(EventModel.id == state.id).first()
            if not model:
                raise ValueError(f"Event with id {state.id} not found")
            # Update mutable fields
            model.channel_id = state.channel_id
            model.status = state.status
            model.title = state.title
            model.description = state.description
            model.banner_url = state.banner_url
            model.price = state.price
            model.supply = state.supply
            model.onchain_event_id = state.onchain_event_id
            db.commit()
            db.refresh(model)
            self.logger.debug("Updated event %s", model.id)
            return model.to_state()

    # Alias for compatibility with existing workflow code
    def update_state(self, state: EventState) -> EventState:
        """Compatibility wrapper that forwards to ``update_event``.
        """
        return self.update_event(state)
