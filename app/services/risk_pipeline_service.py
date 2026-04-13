"""Compute features, risk scores, and market aggregates from ``market_snapshots``."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

import structlog
from sqlmodel import Session

from app.core.config import settings
from app.models.feature_metric import FeatureMetric
from app.models.market_aggregate import MarketAggregate
from app.models.risk_metric import RiskMetric
from app.repositories import (
    aggregate_repository,
    coin_repository,
    feature_repository,
    market_snapshot_repository,
    risk_repository,
)
from app.services.feature_engineering.feature_service import compute_features
from app.services.ingestion.coingecko_client import fetch_global_market
from app.services.risk_engine.risk_config import compute_config_hash, get_risk_weights
from app.services.risk_engine.risk_scorer import score_risk

logger = structlog.get_logger()


async def run_risk_pipeline(*, session: Session) -> dict[str, int]:
    """Load ticks, compute 7d/30d features, score risk, persist aggregates."""
    coins = coin_repository.list_coins(session=session, limit=100)
    if not coins:
        logger.warning("risk_pipeline_no_coins")
        return {"features": 0, "risks": 0}

    weights = get_risk_weights()
    config_hash = compute_config_hash(weights)
    model_ver = settings.RISK_MODEL_VERSION
    now = datetime.now(UTC)
    since_7d = market_snapshot_repository.window_start_utc(days=7)
    since_30d = market_snapshot_repository.window_start_utc(days=30)

    feature_rows: list[FeatureMetric] = []
    risk_rows: list[RiskMetric] = []
    vols_7d: list[float] = []
    latest_ticks = []

    for coin in coins:
        snaps_7d = market_snapshot_repository.get_snapshots_for_coin(
            session=session,
            coin_id=coin.id,
            since=since_7d,
            oldest_first=True,
            limit=4000,
        )
        snaps_30d = market_snapshot_repository.get_snapshots_for_coin(
            session=session,
            coin_id=coin.id,
            since=since_30d,
            oldest_first=True,
            limit=12000,
        )

        def _prices(snaps: list) -> list[float]:
            return [float(s.price_usd) for s in snaps]

        p7 = _prices(snaps_7d)
        p30 = _prices(snaps_30d)

        f7 = compute_features(p7) if len(p7) >= 2 else None
        f30 = compute_features(p30) if len(p30) >= 2 else None

        if f7:
            feature_rows.append(
                FeatureMetric(
                    coin_id=coin.id,
                    volatility=Decimal(str(f7.volatility)),
                    drawdown=Decimal(str(f7.max_drawdown)),
                    avg_return=Decimal(str(f7.avg_return)),
                    window="7d",
                    computed_at=now,
                )
            )
            vols_7d.append(f7.volatility)

        if f30:
            feature_rows.append(
                FeatureMetric(
                    coin_id=coin.id,
                    volatility=Decimal(str(f30.volatility)),
                    drawdown=Decimal(str(f30.max_drawdown)),
                    avg_return=Decimal(str(f30.avg_return)),
                    window="30d",
                    computed_at=now,
                )
            )

        tick = market_snapshot_repository.get_latest_tick(session=session, coin_id=coin.id)
        if tick:
            latest_ticks.append(tick)

        if f7:
            result = score_risk(f7.volatility, f7.max_drawdown, f7.avg_return)
            risk_rows.append(
                RiskMetric(
                    coin_id=coin.id,
                    risk_score=Decimal(str(result.risk_score)),
                    risk_level=result.risk_level.value,
                    model_version=model_ver,
                    config_hash=config_hash,
                    computed_at=now,
                )
            )

    if risk_rows:
        scores = [float(m.risk_score) for m in risk_rows]
        avg_r = sum(scores) / len(scores)
        high_c = sum(1 for s in scores if s > 50.0)
        ext_c = sum(1 for s in scores if s > 75.0)
    else:
        avg_r, high_c, ext_c = 0.0, 0, 0

    pos = sum(
        1
        for t in latest_ticks
        if t.percent_change_24h is not None and float(t.percent_change_24h) > 0.0
    )
    denom = len(latest_ticks)
    breadth: Decimal | None = (Decimal(pos) / Decimal(denom)) if denom else None

    mvol: Decimal | None = None
    if vols_7d:
        mvol = Decimal(str(sum(vols_7d) / len(vols_7d)))

    btc_dom: Decimal | None = None
    try:
        g = await fetch_global_market()
        data = g.get("data") or {}
        mcp = data.get("market_cap_percentage") or {}
        if mcp.get("btc") is not None:
            btc_dom = Decimal(str(mcp["btc"]))
    except Exception:
        logger.exception("risk_pipeline_global_fetch_failed")

    feature_repository.save_features(session=session, rows=feature_rows)
    risk_repository.save_risk_metrics(session=session, metrics=risk_rows)

    agg = MarketAggregate(
        avg_risk_score=Decimal(str(round(avg_r, 4))),
        high_risk_count=high_c,
        extreme_risk_count=ext_c,
        breadth_ratio=breadth,
        market_volatility=mvol,
        btc_dominance=btc_dom,
        timestamp=now,
    )
    aggregate_repository.save_aggregate(session=session, row=agg)
    session.commit()

    logger.info(
        "risk_pipeline_complete",
        features=len(feature_rows),
        risks=len(risk_rows),
    )
    return {"features": len(feature_rows), "risks": len(risk_rows)}
