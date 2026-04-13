"""Ingestion orchestration — market ticks + risk pipeline (manual / scheduled)."""

from __future__ import annotations

import structlog
from sqlmodel import Session

from app.services.ingestion.market_ingestion import run_market_ingestion
from app.services.ingestion.metadata_loader import ensure_top_coins_loaded
from app.services.risk_pipeline_service import run_risk_pipeline

logger = structlog.get_logger()


async def run_full_ingestion_cycle(*, session: Session) -> dict:
    """Bootstrap coins if needed, ingest market snapshots, compute risk + aggregates."""
    logger.info("ingestion_cycle_stage_start", stage="ensure_top_coins_loaded")
    await ensure_top_coins_loaded(session=session)
    logger.info("ingestion_cycle_stage_complete", stage="ensure_top_coins_loaded")

    logger.info("ingestion_cycle_stage_start", stage="market_ingestion")
    try:
        m = await run_market_ingestion(session=session)
    except Exception:
        logger.exception("ingestion_cycle_stage_failed", stage="market_ingestion")
        raise
    logger.info("ingestion_cycle_stage_complete", stage="market_ingestion")

    logger.info("ingestion_cycle_stage_start", stage="risk_pipeline")
    try:
        r = await run_risk_pipeline(session=session)
    except Exception:
        logger.exception("ingestion_cycle_stage_failed", stage="risk_pipeline")
        raise
    logger.info("ingestion_cycle_stage_complete", stage="risk_pipeline")

    return {**{k: v for k, v in m.items()}, **r}


async def run_ingestion(*, session: Session) -> dict:
    """Backward-compatible name: full cycle (used by API trigger)."""
    return await run_full_ingestion_cycle(session=session)
