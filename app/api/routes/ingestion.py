"""Ingestion API endpoints."""

from typing import Any

from fastapi import APIRouter

from app.api.deps import SessionDep
from app.services.ingestion.ingestion_service import run_ingestion

router = APIRouter(tags=["ingestion"])


@router.post("/trigger-ingestion", summary="Trigger Data Ingestion")
async def trigger_ingestion(session: SessionDep) -> dict[str, Any]:
    """Force an immediate ingestion cycle to fetch data from CoinGecko, compute risk metrics, and store to DB.
    
    This is identical to the recurrent background worker task but triggered synchronously.
    """
    return await run_ingestion(session=session)
