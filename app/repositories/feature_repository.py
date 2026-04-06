"""Repository for feature_metrics."""

from __future__ import annotations

from sqlmodel import Session

from app.models.feature_metric import FeatureMetric


def save_features(*, session: Session, rows: list[FeatureMetric]) -> None:
    """Insert a batch of feature rows (caller commits)."""
    for row in rows:
        session.add(row)
