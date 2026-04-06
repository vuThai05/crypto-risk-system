"""Top risky assets endpoint — coins with the highest risk scores."""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import SessionDep
from app.models.coin import CoinPublic
from app.models.risk_metric import RiskMetricPublic
from app.repositories import coin_repository, risk_repository
from sqlmodel import SQLModel

router = APIRouter(tags=["risk"])


class RiskyAsset(SQLModel):
    """Combined coin info + risk metric for the top-risky-assets response."""

    coin: CoinPublic
    risk: RiskMetricPublic


@router.get("/top-risky-assets", response_model=list[RiskyAsset])
def get_top_risky_assets(
    session: SessionDep,
    limit: int = Query(default=10, ge=1, le=100, description="Number of results"),
) -> list[RiskyAsset]:
    """Return the top N coins with the highest risk scores.

    Each result includes coin metadata and the latest risk metric.
    """
    metrics = risk_repository.get_top_risky_assets(session=session, limit=limit)

    results: list[RiskyAsset] = []
    for metric in metrics:
        coin = coin_repository.get_coin_by_id(session=session, coin_id=metric.coin_id)
        if coin:
            results.append(
                RiskyAsset(
                    coin=CoinPublic.model_validate(coin),
                    risk=RiskMetricPublic.model_validate(metric),
                )
            )

    return results
