"""Feature engineering — pure functions that convert price data into risk features.

All functions in this module are **pure**: they take data in and return results
without touching the database or any external state.  This makes them trivially
unit-testable and deterministic.

Features computed:
    - volatility (annualised standard deviation of log-returns)
    - max drawdown (worst peak-to-trough decline, 0–1)
    - average return (mean of percentage changes)
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class RiskFeatures:
    """Container for computed risk features."""

    volatility: float
    max_drawdown: float
    avg_return: float


def compute_volatility(prices: list[float]) -> float:
    """Compute annualised volatility from a price series.

    Method: standard deviation of log-returns × √365 (crypto trades 365 d/yr).

    Args:
        prices: Chronologically ordered prices (oldest first).

    Returns:
        Annualised volatility as a positive float. Returns 0.0 when
        fewer than 2 prices are available.
    """
    if len(prices) < 2:
        return 0.0

    log_returns = []
    for i in range(1, len(prices)):
        if prices[i - 1] <= 0 or prices[i] <= 0:
            continue
        log_returns.append(math.log(prices[i] / prices[i - 1]))

    if len(log_returns) < 2:
        return 0.0

    mean = sum(log_returns) / len(log_returns)
    variance = sum((r - mean) ** 2 for r in log_returns) / (len(log_returns) - 1)
    std_dev = math.sqrt(variance)

    # Annualise (crypto markets run 365 days)
    return std_dev * math.sqrt(365)


def compute_max_drawdown(prices: list[float]) -> float:
    """Compute maximum drawdown (peak-to-trough decline).

    Args:
        prices: Chronologically ordered prices (oldest first).

    Returns:
        Drawdown as a value between 0.0 (no drawdown) and 1.0 (100% loss).
        Returns 0.0 when fewer than 2 prices are available.
    """
    if len(prices) < 2:
        return 0.0

    peak = prices[0]
    max_dd = 0.0

    for price in prices[1:]:
        if price > peak:
            peak = price
        elif peak > 0:
            drawdown = (peak - price) / peak
            max_dd = max(max_dd, drawdown)

    return max_dd


def compute_avg_return(prices: list[float]) -> float:
    """Compute average percentage return from a price series.

    Args:
        prices: Chronologically ordered prices (oldest first).

    Returns:
        Mean percentage change (e.g., 0.05 = 5%).
        Returns 0.0 when fewer than 2 prices are available.
    """
    if len(prices) < 2:
        return 0.0

    pct_changes = []
    for i in range(1, len(prices)):
        if prices[i - 1] <= 0:
            continue
        pct_changes.append((prices[i] - prices[i - 1]) / prices[i - 1])

    if not pct_changes:
        return 0.0

    return sum(pct_changes) / len(pct_changes)


def compute_features(prices: list[float]) -> RiskFeatures | None:
    """Compute all risk features from a price series.

    Args:
        prices: Chronologically ordered prices (oldest first).

    Returns:
        RiskFeatures dataclass, or None if insufficient data.
    """
    if len(prices) < 2:
        return None

    return RiskFeatures(
        volatility=compute_volatility(prices),
        max_drawdown=compute_max_drawdown(prices),
        avg_return=compute_avg_return(prices),
    )
