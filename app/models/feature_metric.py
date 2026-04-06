"""Persisted feature vectors for risk modelling (table: feature_metrics)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Index, Numeric
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FeatureMetric(SQLModel, table=True):
    """Volatility / drawdown / return features for a window (7d or 30d)."""

    __tablename__ = "feature_metrics"
    __table_args__ = (Index("ix_feature_coin_window", "coin_id", "window"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    coin_id: uuid.UUID = Field(foreign_key="coins.id", index=True)
    volatility: Decimal = Field(sa_column=Column(Numeric(18, 10), nullable=False))
    drawdown: Decimal = Field(sa_column=Column(Numeric(18, 10), nullable=False))
    avg_return: Decimal = Field(sa_column=Column(Numeric(18, 10), nullable=False))
    window: str = Field(max_length=8, index=True)  # "7d" | "30d"
    computed_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
        index=True,
    )


class FeatureMetricPublic(SQLModel):
    """Public representation of computed features."""

    id: uuid.UUID
    coin_id: uuid.UUID
    volatility: Decimal
    drawdown: Decimal
    avg_return: Decimal
    window: str
    computed_at: datetime
