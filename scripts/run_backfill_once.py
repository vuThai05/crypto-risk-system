#!/usr/bin/env python3
"""One-shot weekly backfill for GitHub Actions.

Re-fetches maximum available historical OHLCV data (deduped on insert),
then exits. Designed for weekly cron in CI environments.
"""

from __future__ import annotations

import asyncio
import sys

import structlog

from app.core.config import settings
from app.core.db import engine, init_db_if_enabled
from app.services.ingestion.backfill_service import run_weekly_backfill
from app.services.ingestion.metadata_loader import ensure_top_coins_loaded
from app.utils.logging import setup_logging

from sqlmodel import Session

logger = structlog.get_logger()


async def main() -> None:
    setup_logging(
        log_level="INFO",
        json_output=settings.ENVIRONMENT != "local",
    )
    init_db_if_enabled()

    logger.info("oneshot_backfill_start")

    with Session(engine) as session:
        await ensure_top_coins_loaded(session=session)
        session.commit()

    with Session(engine) as session:
        result = await run_weekly_backfill(session=session)
        logger.info("oneshot_backfill_complete", **result)

    logger.info("oneshot_backfill_exit")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"❌ FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
