"""Weekly historical backfill — longer ``market_chart`` window, idempotent inserts."""

from __future__ import annotations

from sqlmodel import Session

import structlog

from app.services.ingestion.ohlcv_ingestion import run_ohlcv_ingestion

logger = structlog.get_logger()


async def run_weekly_backfill(*, session: Session) -> dict[str, int]:
    """Re-fetch a long window of OHLCV data (deduped by unique constraint)."""
    # CoinGecko free tier: ``max`` is often 365; string triggers maximum available.
    result = await run_ohlcv_ingestion(session=session, days="max")
    logger.info("weekly_backfill_complete", **result)
    return result
