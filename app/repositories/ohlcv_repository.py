"""Repository for ohlcv_candles."""

from __future__ import annotations

import structlog
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session

from app.models.ohlcv_candle import OhlcvCandle

logger = structlog.get_logger()


def insert_candles(*, session: Session, rows: list[dict]) -> int:
    """Bulk-insert OHLCV bars; skip on (coin_id, timeframe, timestamp) conflict."""
    if not rows:
        return 0

    stmt = pg_insert(OhlcvCandle).values(rows)
    stmt = stmt.on_conflict_do_nothing(constraint="uq_ohlcv_coin_tf_ts")
    result = session.exec(stmt)  # type: ignore[call-overload]
    inserted = result.rowcount  # type: ignore[union-attr]
    logger.info("ohlcv_insert_complete", inserted=inserted, total=len(rows))
    return inserted
