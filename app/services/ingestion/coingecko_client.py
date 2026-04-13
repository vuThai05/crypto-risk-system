"""CoinGecko API client — HTTP, retries, and response normalization."""

from __future__ import annotations

import asyncio
import time
from collections import deque
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger()

_TIMEOUT = httpx.Timeout(45.0, connect=15.0)
_MAX_RETRIES = 3
_RATE_LIMIT_LOCK = asyncio.Lock()
_REQUEST_TIMESTAMPS: deque[float] = deque()


def _build_headers() -> dict[str, str]:
    headers = {"Accept": "application/json"}
    if settings.COINGECKO_API_KEY:
        headers["x-cg-demo-api-key"] = settings.COINGECKO_API_KEY
    return headers


async def _acquire_rate_limit_slot() -> None:
    """Global token bucket (sliding window) shared by all CoinGecko endpoints."""
    rpm = max(1, settings.COINGECKO_MAX_REQUESTS_PER_MINUTE)
    window_s = 60.0

    while True:
        async with _RATE_LIMIT_LOCK:
            now = time.monotonic()

            # Drop entries that are outside the 60s window.
            while _REQUEST_TIMESTAMPS and (now - _REQUEST_TIMESTAMPS[0]) >= window_s:
                _REQUEST_TIMESTAMPS.popleft()

            if len(_REQUEST_TIMESTAMPS) < rpm:
                _REQUEST_TIMESTAMPS.append(now)
                return

            wait_s = window_s - (now - _REQUEST_TIMESTAMPS[0])

        # Sleep outside the lock to allow other coroutines to progress.
        await asyncio.sleep(max(wait_s, 0.01))


async def _request_json(method: str, url: str, **kwargs: Any) -> Any:
    """HTTP request with exponential backoff (max 3 attempts)."""
    last_exc: Exception | None = None
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for attempt in range(_MAX_RETRIES):
            try:
                await _acquire_rate_limit_slot()
                response = await client.request(method, url, headers=_build_headers(), **kwargs)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                status_code = e.response.status_code
                # Auth / non-retryable client errors should fail fast.
                if status_code in {401, 403}:
                    logger.error(
                        "coingecko_request_auth_failed",
                        url=url,
                        status_code=status_code,
                        error=str(e),
                    )
                    raise
                # Retry 429 (rate-limited), fail fast for other non-auth 4xx.
                elif 400 <= status_code < 500 and status_code != 429:
                    logger.error(
                        "coingecko_request_client_failed",
                        url=url,
                        status_code=status_code,
                        error=str(e),
                    )
                    raise
                last_exc = e
                wait_s = 2**attempt
                logger.warning(
                    "coingecko_request_retry",
                    url=url,
                    attempt=attempt + 1,
                    wait_s=wait_s,
                    error=str(e),
                )
                await asyncio.sleep(wait_s)
            except httpx.HTTPError as e:
                last_exc = e
                wait_s = 2**attempt
                logger.warning(
                    "coingecko_request_retry",
                    url=url,
                    attempt=attempt + 1,
                    wait_s=wait_s,
                    error=str(e),
                )
                await asyncio.sleep(wait_s)
    assert last_exc is not None
    logger.error("coingecko_request_failed", url=url, error=str(last_exc))
    raise last_exc


async def fetch_top_coins(
    per_page: int = 100,
    page: int = 1,
    vs_currency: str = "usd",
) -> list[dict[str, Any]]:
    """``GET /coins/markets`` — top coins by market cap."""
    url = f"{settings.COINGECKO_API_URL}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "page": page,
        "sparkline": "false",
        "price_change_percentage": "1h,24h,7d",
    }
    logger.info("coingecko_fetch_markets", per_page=per_page, page=page)
    data = await _request_json("GET", url, params=params)
    if not isinstance(data, list):
        raise ValueError(f"Expected list from CoinGecko markets, got {type(data).__name__}")
    return data


def _extract_pct_change(raw: dict[str, Any], suffix: str) -> float | None:
    """Read 1h / 24h / 7d percentage fields (CoinGecko shape varies slightly)."""
    keys = [
        f"price_change_percentage_{suffix}",
        f"price_change_percentage_{suffix}_in_currency",
    ]
    for key in keys:
        val = raw.get(key)
        if val is None:
            continue
        if isinstance(val, dict):
            inner = val.get("usd") or next(iter(val.values()), None) if val else None
            if inner is not None:
                return float(inner)
        else:
            return float(val)
    return None


def validate_coin_data(raw: dict[str, Any]) -> dict[str, Any] | None:
    """Validate and normalize one coin from ``/coins/markets``."""
    required_fields = ["id", "symbol", "name", "current_price"]
    for field in required_fields:
        if field not in raw or raw[field] is None:
            logger.warning("coingecko_invalid_coin", missing_field=field, raw_id=raw.get("id"))
            return None

    return {
        "coingecko_id": raw["id"],
        "symbol": str(raw["symbol"]).lower(),
        "name": raw["name"],
        "market_cap_rank": raw.get("market_cap_rank"),
        "image_url": raw.get("image"),
        "current_price": float(raw["current_price"]),
        "market_cap": float(raw["market_cap"]) if raw.get("market_cap") is not None else None,
        "total_volume": float(raw["total_volume"]) if raw.get("total_volume") is not None else None,
        "percent_change_1h": _extract_pct_change(raw, "1h"),
        "percent_change_24h": _extract_pct_change(raw, "24h"),
        "percent_change_7d": _extract_pct_change(raw, "7d"),
    }


async def fetch_market_chart(
    coingecko_id: str,
    *,
    vs_currency: str = "usd",
    days: str | float = 90,
) -> dict[str, Any]:
    """``GET /coins/{id}/market_chart`` — prices and volumes time series."""
    url = f"{settings.COINGECKO_API_URL}/coins/{coingecko_id}/market_chart"
    params: dict[str, Any] = {"vs_currency": vs_currency, "days": days}
    return await _request_json("GET", url, params=params)


async def fetch_global_market() -> dict[str, Any]:
    """``GET /global`` — market cap percentages (BTC dominance, etc.)."""
    url = f"{settings.COINGECKO_API_URL}/global"
    return await _request_json("GET", url)
