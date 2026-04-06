"""RiskMetric model — computed risk scores for each coin (table: risk_metrics)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RiskLevel(StrEnum):
    """Risk classification based on score thresholds."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    EXTREME = "Extreme"


class RiskMetric(SQLModel, table=True):
    """Computed risk score for a coin (features live in ``feature_metrics``)."""

    __tablename__ = "risk_metrics"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    coin_id: uuid.UUID = Field(foreign_key="coins.id", index=True)
    risk_score: Decimal = Field(sa_column=Column(Numeric(10, 4), nullable=False))
    risk_level: str = Field(max_length=32)
    model_version: str = Field(default="1.0.0", max_length=32)
    config_hash: str = Field(default="", max_length=64)
    computed_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
        index=True,
    )


class RiskMetricPublic(SQLModel):
    """Public representation of a risk metric."""

    id: uuid.UUID
    coin_id: uuid.UUID
    risk_score: Decimal
    risk_level: str
    model_version: str
    config_hash: str
    computed_at: datetime


class RiskMetricsPublic(SQLModel):
    """Paginated list of risk metrics."""

    data: list[RiskMetricPublic]
    count: int
