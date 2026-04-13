"""OHLCV ingestion — ``market_chart`` → 12h candles in ``ohlcv_candles``."""

from __future__ import annotations

import asyncio
import uuid
from collections import defaultdict
from datetime import UTC, datetime
from decimal import Decimal

import httpx
import structlog
from sqlalchemy.exc import OperationalError
from sqlmodel import Session

from app.core.db import engine
from app.repositories import coin_repository, ohlcv_repository
from app.services.ingestion.coingecko_client import fetch_market_chart

logger = structlog.get_logger()

TIMEFRAME = "12h"
TWELVE_H_MS = 12 * 60 * 60 * 1000


def _bucket_ohlcv(
    prices: list[list],
    volumes: list[list],
) -> list[tuple[int, Decimal, Decimal, Decimal, Decimal, Decimal | None]]:
    """Return list of (bucket_start_ms, open, high, low, close, volume_sum)."""
    by_bucket: dict[int, list[tuple[int, Decimal, Decimal]]] = defaultdict(list)

    for i, pair in enumerate(prices):
        if not pair or len(pair) < 2:
            continue
        ts_ms, price = int(pair[0]), Decimal(str(pair[1]))
        vol = Decimal(str(volumes[i][1])) if i < len(volumes) and len(volumes[i]) >= 2 else None
        b = (ts_ms // TWELVE_H_MS) * TWELVE_H_MS
        v = vol if vol is not None else Decimal("0")
        by_bucket[b].append((ts_ms, price, v))

    out: list[tuple[int, Decimal, Decimal, Decimal, Decimal, Decimal | None]] = []
    for b_start in sorted(by_bucket.keys()):
        pts = sorted(by_bucket[b_start], key=lambda x: x[0])
        if not pts:
            continue
        o = pts[0][1]
        c = pts[-1][1]
        hi = max(p[1] for p in pts)
        lo = min(p[1] for p in pts)
        vol_sum = sum((p[2] for p in pts), Decimal("0"))
        out.append((b_start, o, hi, lo, c, vol_sum if vol_sum > 0 else None))
    return out


async def run_ohlcv_ingestion(*, session: Session, days: float | str = 90) -> dict[str, int]:
    """Fetch market charts for each tracked coin and upsert 12h OHLCV bars."""
    coins = coin_repository.list_coins(session=session, limit=100)
    # Release connection before starting long-running external API loop.
    session.close()
    total_inserted = 0

    for coin in coins:
        try:
            chart = await fetch_market_chart(coin.coingecko_id, days=days)
        except Exception as exc:
            if isinstance(exc, httpx.HTTPStatusError):
                if exc.response.status_code in {401, 403}:
                    raise
                # HTTP errors are already logged in the client; add coin context and skip.
                logger.warning(
                    "ohlcv_chart_http_skipped",
                    coingecko_id=coin.coingecko_id,
                    status_code=exc.response.status_code,
                )
                continue
            logger.exception("ohlcv_chart_failed", coingecko_id=coin.coingecko_id)
            continue

        prices = chart.get("prices") or []
        volumes = chart.get("total_volumes") or []
        if len(prices) < 2:
            continue

        bars = _bucket_ohlcv(prices, volumes)
        rows: list[dict] = []
        for b_start_ms, o, hi, lo, c, vol in bars:
            ts = datetime.fromtimestamp(b_start_ms / 1000.0, tz=UTC)
            rows.append(
                {
                    "id": uuid.uuid4(),
                    "coin_id": coin.id,
                    "timeframe": TIMEFRAME,
                    "open_price": o,
                    "high_price": hi,
                    "low_price": lo,
                    "close_price": c,
                    "volume": vol,
                    "timestamp": ts,
                }
            )

        inserted_for_coin = 0
        for attempt in range(1, 4):
            try:
                with Session(engine) as write_session:
                    inserted_for_coin = ohlcv_repository.insert_candles(
                        session=write_session,
                        rows=rows,
                    )
                    write_session.commit()
                break
            except OperationalError as exc:
                if attempt == 3:
                    logger.exception(
                        "ohlcv_db_insert_failed",
                        coingecko_id=coin.coingecko_id,
                        attempts=attempt,
                        error=str(exc),
                    )
                    inserted_for_coin = 0
                    break
                wait_s = float(attempt)
                logger.warning(
                    "ohlcv_db_insert_retry",
                    coingecko_id=coin.coingecko_id,
                    attempt=attempt,
                    wait_s=wait_s,
                    error=str(exc),
                )
                await asyncio.sleep(wait_s)

        total_inserted += inserted_for_coin

    logger.info("ohlcv_ingestion_complete", candles_inserted=total_inserted, coins=len(coins))
    return {"candles_inserted": total_inserted, "coins": len(coins)}
