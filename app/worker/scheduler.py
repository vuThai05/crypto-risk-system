"""Background worker — market + risk cycle, OHLCV, weekly backfill.

Run as a separate process (not inside FastAPI). See ``scripts/run_worker.py``.
"""

from __future__ import annotations

import asyncio

import structlog
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db_if_enabled
from app.services.ingestion.backfill_service import run_weekly_backfill
from app.services.ingestion.ingestion_service import run_full_ingestion_cycle
from app.services.ingestion.metadata_loader import ensure_top_coins_loaded
from app.services.ingestion.ohlcv_ingestion import run_ohlcv_ingestion
from app.utils.logging import setup_logging

logger = structlog.get_logger()


async def _market_risk_loop() -> None:
    interval_s = settings.INGESTION_INTERVAL_MINUTES * 60
    logger.info("worker_market_loop_started", interval_minutes=settings.INGESTION_INTERVAL_MINUTES)
    while True:
        try:
            with Session(engine) as session:
                await run_full_ingestion_cycle(session=session)
        except Exception:
            logger.exception("worker_market_cycle_failed")
        await asyncio.sleep(interval_s)


async def _ohlcv_loop() -> None:
    interval_s = settings.OHLCV_INTERVAL_HOURS * 3600
    logger.info("worker_ohlcv_loop_started", interval_hours=settings.OHLCV_INTERVAL_HOURS)
    while True:
        try:
            with Session(engine) as session:
                await run_ohlcv_ingestion(session=session)
        except Exception:
            logger.exception("worker_ohlcv_failed")
        await asyncio.sleep(interval_s)


async def _backfill_loop() -> None:
    interval_s = settings.BACKFILL_INTERVAL_DAYS * 86400
    logger.info(
        "worker_backfill_loop_started",
        interval_days=settings.BACKFILL_INTERVAL_DAYS,
    )
    while True:
        await asyncio.sleep(interval_s)
        try:
            with Session(engine) as session:
                await run_weekly_backfill(session=session)
        except Exception:
            logger.exception("worker_backfill_failed")


async def run_worker() -> None:
    """Entry point: init DB, seed coins if empty, then run scheduled loops."""
    setup_logging(
        log_level="DEBUG" if settings.ENVIRONMENT == "local" else "INFO",
        json_output=settings.ENVIRONMENT != "local",
    )
    init_db_if_enabled()
    with Session(engine) as session:
        await ensure_top_coins_loaded(session=session)
        session.commit()

    await asyncio.gather(
        _market_risk_loop(),
        _ohlcv_loop(),
        _backfill_loop(),
    )


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
