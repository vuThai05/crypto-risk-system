"""Market-wide aggregates (table: market_aggregates)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Numeric
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MarketAggregate(SQLModel, table=True):
    """Aggregated risk and market structure metrics across tracked coins."""

    __tablename__ = "market_aggregates"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    avg_risk_score: Decimal = Field(sa_column=Column(Numeric(10, 4), nullable=False))
    high_risk_count: int = Field(default=0)
    extreme_risk_count: int = Field(default=0)
    breadth_ratio: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 6)))
    market_volatility: Decimal | None = Field(default=None, sa_column=Column(Numeric(18, 8)))
    btc_dominance: Decimal | None = Field(default=None, sa_column=Column(Numeric(10, 6)))
    timestamp: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
        index=True,
    )


class MarketAggregatePublic(SQLModel):
    """Public API representation of the latest aggregate row."""

    id: uuid.UUID
    avg_risk_score: Decimal
    high_risk_count: int
    extreme_risk_count: int
    breadth_ratio: Decimal | None
    market_volatility: Decimal | None
    btc_dominance: Decimal | None
    timestamp: datetime
