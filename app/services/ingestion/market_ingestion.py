"""Market tick ingestion — ``/coins/markets`` → ``market_snapshots``."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from decimal import Decimal

import structlog
from sqlmodel import Session

from app.core.db import engine
from app.repositories import coin_repository, market_snapshot_repository
from app.services.ingestion.coingecko_client import fetch_top_coins, validate_coin_data

logger = structlog.get_logger()


async def run_market_ingestion(*, session: Session) -> dict[str, int | str]:
    """Fetch markets, insert idempotent rows into ``market_snapshots`` for known coins.

    Does not upsert ``coins`` on every run (metadata lives in ``metadata_loader``).
    Rows that reference unknown ``coingecko_id`` are skipped.
    """
    # Caller keeps orchestration ownership; this function opens a short-lived
    # write session to avoid reusing stale pooled connections after network I/O.

    now = datetime.now(UTC)
    raw = await fetch_top_coins(per_page=100)
    with Session(engine) as write_session:
        cg_to_coin = {
            c.coingecko_id: c.id
            for c in coin_repository.list_coins(session=write_session, limit=200)
        }

        rows: list[dict] = []
        for item in raw:
            v = validate_coin_data(item)
            if not v:
                continue
            cid = cg_to_coin.get(v["coingecko_id"])
            if not cid:
                continue

            def _d(x: float | None) -> Decimal | None:
                if x is None:
                    return None
                return Decimal(str(x))

            rows.append(
                {
                    "id": uuid.uuid4(),
                    "coin_id": cid,
                    "price_usd": _d(v["current_price"]),
                    "market_cap": _d(v["market_cap"]),
                    "volume_24h": _d(v["total_volume"]),
                    "percent_change_1h": _d(v.get("percent_change_1h")),
                    "percent_change_24h": _d(v.get("percent_change_24h")),
                    "percent_change_7d": _d(v.get("percent_change_7d")),
                    "timestamp": now,
                }
            )

        inserted = market_snapshot_repository.insert_snapshots(session=write_session, rows=rows)
        write_session.commit()

    summary = {"snapshots_inserted": inserted, "timestamp": now.isoformat()}
    logger.info("market_ingestion_complete", **summary)
    return summary
