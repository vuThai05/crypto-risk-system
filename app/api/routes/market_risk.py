"""Market risk endpoint — aggregate risk across the top-100 market."""

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.market_aggregate import MarketAggregatePublic
from app.repositories import aggregate_repository

router = APIRouter(tags=["risk"])


@router.get("/market-risk", response_model=MarketAggregatePublic)
def get_market_risk(session: SessionDep) -> MarketAggregatePublic:
    """Return the latest market-wide aggregate (risk, breadth, BTC dominance)."""
    row = aggregate_repository.get_latest_aggregate(session=session)
    if not row:
        raise HTTPException(
            status_code=404,
            detail="No market aggregate yet. Run the worker or POST trigger-ingestion.",
        )
    return MarketAggregatePublic.model_validate(row)
