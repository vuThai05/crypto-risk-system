"""Coin model — represents a tracked cryptocurrency."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# Database table
# ---------------------------------------------------------------------------

class Coin(SQLModel, table=True):
    """A cryptocurrency tracked by the system (top-100 by market cap)."""

    __tablename__ = "coins"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    coingecko_id: str = Field(unique=True, index=True, max_length=128)
    symbol: str = Field(max_length=32)
    name: str = Field(max_length=256)
    market_cap_rank: int | None = Field(default=None, index=True)
    image_url: str | None = Field(default=None, max_length=512)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_type=DateTime(timezone=True),  # type: ignore[call-overload]
    )


# ---------------------------------------------------------------------------
# API schemas
# ---------------------------------------------------------------------------

class CoinCreate(SQLModel):
    """Payload used internally when upserting coins from CoinGecko data."""

    coingecko_id: str
    symbol: str
    name: str
    market_cap_rank: int | None = None
    image_url: str | None = None


class CoinPublic(SQLModel):
    """Public representation returned by the API."""

    id: uuid.UUID
    coingecko_id: str
    symbol: str
    name: str
    market_cap_rank: int | None = None
    image_url: str | None = None


class CoinsPublic(SQLModel):
    """Paginated list of coins."""

    data: list[CoinPublic]
    count: int
