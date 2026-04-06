"""Risk metrics repository — data-access for the risk_metrics table."""

from __future__ import annotations

import uuid

from sqlmodel import Session, select

from app.models.risk_metric import RiskMetric


def save_risk_metric(*, session: Session, metric: RiskMetric) -> RiskMetric:
    """Persist a computed risk metric (caller ``commit``)."""
    session.add(metric)
    session.flush()
    session.refresh(metric)
    return metric


def save_risk_metrics(
    *, session: Session, metrics: list[RiskMetric]
) -> list[RiskMetric]:
    """Persist a batch of risk metrics (caller ``commit``)."""
    for m in metrics:
        session.add(m)
    session.flush()
    for m in metrics:
        session.refresh(m)
    return metrics


def get_latest_risk(
    *, session: Session, coin_id: uuid.UUID
) -> RiskMetric | None:
    """Get the most recent risk metric for a coin."""
    statement = (
        select(RiskMetric)
        .where(RiskMetric.coin_id == coin_id)
        .order_by(RiskMetric.computed_at.desc())  # type: ignore[union-attr]
        .limit(1)
    )
    return session.exec(statement).first()


def get_top_risky_assets(
    *, session: Session, limit: int = 10
) -> list[RiskMetric]:
    """Get the top N highest-risk coins based on the latest risk computation.

    Uses a subquery to find the latest risk metric per coin, then sorts
    by risk_score descending.
    """
    # Get the latest computed_at for each coin
    from sqlalchemy import func

    latest_subquery = (
        select(
            RiskMetric.coin_id,
            func.max(RiskMetric.computed_at).label("max_computed_at"),
        )
        .group_by(RiskMetric.coin_id)
        .subquery()
    )

    statement = (
        select(RiskMetric)
        .join(
            latest_subquery,
            (RiskMetric.coin_id == latest_subquery.c.coin_id)
            & (RiskMetric.computed_at == latest_subquery.c.max_computed_at),
        )
        .order_by(RiskMetric.risk_score.desc())  # type: ignore[union-attr]
        .limit(limit)
    )
    return list(session.exec(statement).all())


def get_all_latest_risks(*, session: Session) -> list[RiskMetric]:
    """Get the latest risk metric for every coin (used for snapshot aggregation)."""
    from sqlalchemy import func

    latest_subquery = (
        select(
            RiskMetric.coin_id,
            func.max(RiskMetric.computed_at).label("max_computed_at"),
        )
        .group_by(RiskMetric.coin_id)
        .subquery()
    )

    statement = select(RiskMetric).join(
        latest_subquery,
        (RiskMetric.coin_id == latest_subquery.c.coin_id)
        & (RiskMetric.computed_at == latest_subquery.c.max_computed_at),
    )
    return list(session.exec(statement).all())
