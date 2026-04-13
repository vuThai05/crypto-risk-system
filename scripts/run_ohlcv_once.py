#!/usr/bin/env python3
"""One-shot OHLCV ingestion for GitHub Actions.

Fetches market charts for tracked coins and upserts 12h OHLCV candles,
then exits. Designed for cron-triggered CI environments (every 12h).
"""

from __future__ import annotations

import asyncio
import sys

import structlog

from app.core.config import settings
from app.core.db import engine, init_db_if_enabled
from app.services.ingestion.metadata_loader import ensure_top_coins_loaded
from app.services.ingestion.ohlcv_ingestion import run_ohlcv_ingestion
from app.utils.logging import setup_logging

from sqlmodel import Session

logger = structlog.get_logger()


async def main() -> None:
    setup_logging(
        log_level="INFO",
        json_output=settings.ENVIRONMENT != "local",
    )
    init_db_if_enabled()

    logger.info("oneshot_ohlcv_start")

    with Session(engine) as session:
        await ensure_top_coins_loaded(session=session)
        session.commit()

    with Session(engine) as session:
        result = await run_ohlcv_ingestion(session=session, days=90)
        logger.info("oneshot_ohlcv_complete", **result)

    logger.info("oneshot_ohlcv_exit")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
