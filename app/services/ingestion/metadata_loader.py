"""Load Top-100 coin metadata once (startup / empty DB)."""

from __future__ import annotations

import structlog
from sqlmodel import Session

from app.models.coin import CoinCreate
from app.repositories import coin_repository
from app.services.ingestion.coingecko_client import fetch_top_coins, validate_coin_data

logger = structlog.get_logger()


async def ensure_top_coins_loaded(*, session: Session) -> dict[str, int | bool]:
    """If ``coins`` is empty, fetch Top 100 from CoinGecko and upsert.

    Per spec, metadata is not refreshed on a daily schedule; call this at worker
    startup (and ingestion uses this when the table is empty).
    """
    existing = coin_repository.count_coins(session=session)
    if existing > 0:
        return {"bootstrapped": False, "coins": existing}

    # Release any checked-out connection before waiting on external API I/O.
    session.close()
    raw = await fetch_top_coins(per_page=100)
    valid = []
    for row in raw:
        v = validate_coin_data(row)
        if v:
            valid.append(v)

    creates = [
        CoinCreate(
            coingecko_id=c["coingecko_id"],
            symbol=c["symbol"],
            name=c["name"],
            market_cap_rank=c["market_cap_rank"],
            image_url=c["image_url"],
        )
        for c in valid
    ]
    db_coins = coin_repository.bulk_upsert_coins(session=session, coins_in=creates)
    session.commit()
    logger.info("metadata_bootstrap_complete", coins=len(db_coins))
    return {"bootstrapped": True, "coins": len(db_coins)}
