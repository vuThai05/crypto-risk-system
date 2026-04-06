"""Repository for market_aggregates rows."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.market_aggregate import MarketAggregate


def save_aggregate(*, session: Session, row: MarketAggregate) -> MarketAggregate:
    """Persist one aggregate snapshot (caller ``commit``)."""
    session.add(row)
    session.flush()
    session.refresh(row)
    return row


def get_latest_aggregate(*, session: Session) -> MarketAggregate | None:
    """Most recent market aggregate."""
    statement = (
        select(MarketAggregate)
        .order_by(MarketAggregate.timestamp.desc())  # type: ignore[union-attr]
        .limit(1)
    )
    return session.exec(statement).first()
