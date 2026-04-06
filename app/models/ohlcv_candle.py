"""OHLCV candles for analytics (table: ohlcv_candles)."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import Column, DateTime, Index, Numeric, UniqueConstraint
from sqlmodel import Field, SQLModel


class OhlcvCandle(SQLModel, table=True):
    """Candlestick bar (e.g. 12h) derived from CoinGecko market chart data."""

    __tablename__ = "ohlcv_candles"
    __table_args__ = (
        UniqueConstraint("coin_id", "timeframe", "timestamp", name="uq_ohlcv_coin_tf_ts"),
        Index("ix_ohlcv_coin_ts", "coin_id", "timestamp"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    coin_id: uuid.UUID = Field(foreign_key="coins.id", index=True)
    timeframe: str = Field(max_length=16, index=True)  # e.g. "12h"
    open_price: Decimal = Field(sa_column=Column(Numeric(28, 12), nullable=False))
    high_price: Decimal = Field(sa_column=Column(Numeric(28, 12), nullable=False))
    low_price: Decimal = Field(sa_column=Column(Numeric(28, 12), nullable=False))
    close_price: Decimal = Field(sa_column=Column(Numeric(28, 12), nullable=False))
    volume: Decimal | None = Field(default=None, sa_column=Column(Numeric(28, 4)))
    timestamp: datetime = Field(
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
        index=True,
    )
