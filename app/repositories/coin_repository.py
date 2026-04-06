"""Coin repository — data-access for the coins table."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

from app.models.coin import Coin, CoinCreate


from sqlalchemy.dialects.postgresql import insert as pg_insert

def bulk_upsert_coins(*, session: Session, coins_in: list[CoinCreate]) -> list[Coin]:
    """Bulk upsert a batch of coins using PostgreSQL ON CONFLICT DO UPDATE.
    No session.commit() is called here; to be managed by caller.

    NOTE: pg_insert RETURNING via session.exec() returns raw Row tuples, not
    SQLModel objects. We therefore run the upsert without RETURNING, then
    re-query the affected rows using a standard SELECT to get proper Coin ORM
    objects with all attributes accessible (e.g. c.coingecko_id, c.id).
    """
    if not coins_in:
        return []

    values = []
    now = datetime.now(timezone.utc)
    coingecko_ids = []
    for coin_in in coins_in:
        coingecko_ids.append(coin_in.coingecko_id)
        values.append(
            {
                "id": uuid.uuid4(),
                "coingecko_id": coin_in.coingecko_id,
                "symbol": coin_in.symbol,
                "name": coin_in.name,
                "market_cap_rank": coin_in.market_cap_rank,
                "image_url": coin_in.image_url,
                "created_at": now,
                "updated_at": now,
            }
        )

    # Run upsert (no RETURNING — avoids Row tuple mismatch with SQLModel)
    stmt = pg_insert(Coin).values(values)
    stmt = stmt.on_conflict_do_update(
        index_elements=["coingecko_id"],
        set_={
            "symbol": stmt.excluded.symbol,
            "name": stmt.excluded.name,
            "market_cap_rank": stmt.excluded.market_cap_rank,
            "image_url": stmt.excluded.image_url,
            "updated_at": stmt.excluded.updated_at,
        },
    )
    session.exec(stmt)  # type: ignore[call-overload]

    # Re-query to return proper SQLModel Coin objects
    result = session.exec(
        select(Coin).where(Coin.coingecko_id.in_(coingecko_ids))  # type: ignore[attr-defined]
    )
    return list(result.all())


def get_coin_by_id(*, session: Session, coin_id: uuid.UUID) -> Coin | None:
    return session.get(Coin, coin_id)


def get_coin_by_coingecko_id(*, session: Session, coingecko_id: str) -> Coin | None:
    statement = select(Coin).where(Coin.coingecko_id == coingecko_id)
    return session.exec(statement).first()


def list_coins(
    *, session: Session, skip: int = 0, limit: int = 100
) -> list[Coin]:
    """List coins ordered by market_cap_rank."""
    statement = (
        select(Coin)
        .order_by(Coin.market_cap_rank)
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


def count_coins(*, session: Session) -> int:
    statement = select(Coin)
    return len(list(session.exec(statement).all()))
