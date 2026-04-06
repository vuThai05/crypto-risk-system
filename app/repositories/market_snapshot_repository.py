"""Repository for per-coin market_snapshots (ingestion ticks)."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
import structlog
from sqlalchemy import asc, desc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, select

from app.models.market_snapshot import MarketSnapshot

logger = structlog.get_logger()


def insert_snapshots(*, session: Session, rows: list[dict]) -> int:
    """Bulk-insert ticks; skip duplicates on (coin_id, timestamp)."""
    if not rows:
        return 0

    stmt = pg_insert(MarketSnapshot).values(rows)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_market_snapshots_coin_timestamp")
    result = session.exec(stmt)  # type: ignore[call-overload]
    inserted = result.rowcount  # type: ignore[union-attr]
    logger.info("market_snapshot_insert_complete", inserted=inserted, total=len(rows))
    return inserted


def get_snapshots_for_coin(
    *,
    session: Session,
    coin_id: uuid.UUID,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 5000,
    oldest_first: bool = False,
) -> list[MarketSnapshot]:
    """Fetch ticks for one coin, optionally bounded in time."""
    statement = select(MarketSnapshot).where(MarketSnapshot.coin_id == coin_id)

    if since:
        statement = statement.where(MarketSnapshot.timestamp >= since)
    if until:
        statement = statement.where(MarketSnapshot.timestamp <= until)

    order = asc(MarketSnapshot.timestamp) if oldest_first else desc(MarketSnapshot.timestamp)
    statement = statement.order_by(order).limit(limit)  # type: ignore[union-attr]
    return list(session.exec(statement).all())


def get_latest_tick(*, session: Session, coin_id: uuid.UUID) -> MarketSnapshot | None:
    """Most recent tick for a coin."""
    statement = (
        select(MarketSnapshot)
        .where(MarketSnapshot.coin_id == coin_id)
        .order_by(desc(MarketSnapshot.timestamp))
        .limit(1)
    )
    return session.exec(statement).first()


def window_start_utc(*, days: int) -> datetime:
    """UTC ``now - days`` for rolling windows."""
    return datetime.now(timezone.utc) - timedelta(days=days)
