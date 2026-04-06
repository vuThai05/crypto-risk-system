"""Coin risk endpoint — risk metrics for individual coins."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException

from app.api.deps import SessionDep
from app.models.risk_metric import RiskMetricPublic
from app.repositories import coin_repository, risk_repository

router = APIRouter(tags=["risk"])


@router.get("/coins/{coin_id}/risk", response_model=RiskMetricPublic)
def get_coin_risk(
    coin_id: uuid.UUID,
    session: SessionDep,
) -> RiskMetricPublic:
    """Return the latest risk metric for a specific coin.

    Args:
        coin_id: UUID of the coin (from the coins table).
    """
    # Verify coin exists
    coin = coin_repository.get_coin_by_id(session=session, coin_id=coin_id)
    if not coin:
        raise HTTPException(status_code=404, detail="Coin not found.")

    metric = risk_repository.get_latest_risk(session=session, coin_id=coin_id)
    if not metric:
        raise HTTPException(
            status_code=404,
            detail=f"No risk data available for coin {coin_id}.",
        )
    return RiskMetricPublic.model_validate(metric)
