"""Per-coin market ticks — core ingestion layer (table: market_snapshots)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Index, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class MarketSnapshot(SQLModel, table=True):
    """Point-in-time market data for one coin (from CoinGecko /coins/markets)."""

    __tablename__ = "market_snapshots"
    __table_args__ = (
        UniqueConstraint("coin_id", "timestamp", name="uq_market_snapshots_coin_timestamp"),
        Index("ix_market_snapshots_coin_ts", "coin_id", "timestamp"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    coin_id: uuid.UUID = Field(foreign_key="coins.id", index=True)
    price_usd: Decimal = Field(sa_column=Column(Numeric(28, 12), nullable=False))
    market_cap: Decimal | None = Field(default=None, sa_column=Column(Numeric(28, 4)))
    volume_24h: Decimal | None = Field(default=None, sa_column=Column(Numeric(28, 4)))
    percent_change_1h: Decimal | None = Field(default=None, sa_column=Column(Numeric(18, 8)))
    percent_change_24h: Decimal | None = Field(default=None, sa_column=Column(Numeric(18, 8)))
    percent_change_7d: Decimal | None = Field(default=None, sa_column=Column(Numeric(18, 8)))
    timestamp: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
        index=True,
    )


class MarketSnapshotPublic(SQLModel):
    """API schema for a single tick (optional, for future endpoints)."""

    id: uuid.UUID
    coin_id: uuid.UUID
    price_usd: Decimal
    market_cap: Decimal | None
    volume_24h: Decimal | None
    percent_change_1h: Decimal | None
    percent_change_24h: Decimal | None
    percent_change_7d: Decimal | None
    timestamp: datetime
