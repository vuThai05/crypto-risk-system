#!/usr/bin/env python3
"""One-shot market ingestion + risk pipeline for GitHub Actions.

Runs a single cycle of:
  1. Ensure top coins loaded
  2. Market data ingestion
  3. Risk pipeline computation

Then exits. Designed for cron-triggered CI environments.
"""

from __future__ import annotations

import asyncio
import sys

import structlog
from sqlmodel import Session

from app.core.config import settings
from app.core.db import engine, init_db_if_enabled, wait_for_db_connection
from app.services.ingestion.ingestion_service import run_full_ingestion_cycle
from app.utils.logging import setup_logging

logger = structlog.get_logger()


async def main() -> None:
    setup_logging(
        log_level="INFO",
        json_output=settings.ENVIRONMENT != "local",
    )
    logger.info("oneshot_market_start")
    wait_for_db_connection()
    init_db_if_enabled()

    with Session(engine) as session:
        result = await run_full_ingestion_cycle(session=session)
        logger.info("oneshot_market_complete", **result)

    logger.info("oneshot_market_exit")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        logger.exception("oneshot_market_failed")
        print(f"FAILED: {exc}", file=sys.stderr)
        sys.exit(1)
