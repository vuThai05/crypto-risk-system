"""Risk scorer — pure functions that convert features into risk scores.

This is the **core** of the system. Every function is pure: takes data in,
returns results, with no side-effects. This guarantees:
    - Deterministic, reproducible results
    - Easy unit-testing
    - No database or I/O coupling

Scoring model:
    1. Normalize each feature to [0, 1]
    2. Compute weighted sum (config-driven weights)
    3. Scale to 0–100 → risk_score
    4. Classify into RiskLevel (Low / Medium / High / Extreme)

Normalization bounds (empirical defaults for crypto markets):
    - Volatility: 0.0 – 3.0 (300% annualised is extreme)
    - Drawdown : 0.0 – 1.0 (already a ratio)
    - Avg Return: −0.5 – +0.5 (inverted: negative returns → higher risk)
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from app.models.risk_metric import RiskLevel
from app.services.risk_engine.risk_config import (
    DEFAULT_THRESHOLDS,
    RiskThresholds,
    RiskWeights,
)


@dataclass(frozen=True)
class RiskResult:
    """Output of the risk scoring pipeline."""

    risk_score: float         # 0–100
    risk_level: RiskLevel
    normalized_volatility: float
    normalized_drawdown: float
    normalized_return: float


# ---------------------------------------------------------------------------
# Normalisation bounds (empirical defaults for crypto markets)
# ---------------------------------------------------------------------------

_VOLATILITY_MIN = 0.0
_VOLATILITY_MAX = 3.0   # 300% annualised vol is extreme

_DRAWDOWN_MIN = 0.0
_DRAWDOWN_MAX = 1.0     # already 0–1

_RETURN_MIN = -0.5       # −50% avg return
_RETURN_MAX = 0.5        # +50% avg return


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    """Clamp a value between lo and hi."""
    return max(lo, min(hi, value))


def _is_valid_number(value: float) -> bool:
    """Check if a value is a finite number (not NaN/Inf)."""
    return math.isfinite(value)


# ---------------------------------------------------------------------------
# Normalisation functions
# ---------------------------------------------------------------------------

def normalize_volatility(volatility: float) -> float:
    """Normalize annualised volatility to [0, 1].

    Higher volatility → higher normalised value → higher risk.

    Edge cases:
        - NaN/Inf → returns 1.0 (assume worst case)
        - Negative → clamped to 0.0
        - Above max (3.0) → clamped to 1.0
    """
    if not _is_valid_number(volatility):
        return 1.0  # assume worst case for corrupt data
    if _VOLATILITY_MAX == _VOLATILITY_MIN:
        return 0.0
    return _clamp((volatility - _VOLATILITY_MIN) / (_VOLATILITY_MAX - _VOLATILITY_MIN))


def normalize_drawdown(drawdown: float) -> float:
    """Normalize max drawdown to [0, 1].

    Higher drawdown → higher normalised value → higher risk.

    Edge cases:
        - NaN/Inf → returns 1.0 (assume worst case)
        - Negative → clamped to 0.0
        - Above 1.0 → clamped to 1.0
    """
    if not _is_valid_number(drawdown):
        return 1.0
    return _clamp(drawdown)


def normalize_return(avg_return: float) -> float:
    """Normalize average return to [0, 1] with **inverted** polarity.

    Negative returns → higher normalised value → higher risk.
    Positive returns → lower normalised value → lower risk.

    Edge cases:
        - NaN/Inf → returns 0.5 (neutral, can't determine direction)
        - Values beyond ±0.5 → clamped to 0.0 or 1.0
    """
    if not _is_valid_number(avg_return):
        return 0.5  # neutral when data is invalid
    if _RETURN_MAX == _RETURN_MIN:
        return 0.5
    raw = (avg_return - _RETURN_MIN) / (_RETURN_MAX - _RETURN_MIN)
    # Invert: good returns (high raw) should lower risk
    return _clamp(1.0 - raw)


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_risk_score(
    volatility: float,
    max_drawdown: float,
    avg_return: float,
    weights: RiskWeights,
) -> float:
    """Compute a composite risk score (0–100).

    Formula: score = (w_v × norm_vol + w_d × norm_dd + w_r × norm_ret) × 100

    The weights are config-driven and must sum to 1.0.
    Each feature is independently normalized to [0, 1] before weighting.
    """
    n_vol = normalize_volatility(volatility)
    n_dd = normalize_drawdown(max_drawdown)
    n_ret = normalize_return(avg_return)

    raw = (
        weights.volatility * n_vol
        + weights.drawdown * n_dd
        + weights.avg_return * n_ret
    )

    return _clamp(raw * 100.0, 0.0, 100.0)


def classify_risk_level(
    score: float,
    thresholds: RiskThresholds = DEFAULT_THRESHOLDS,
) -> RiskLevel:
    """Classify a numeric score into a RiskLevel.

    Boundaries (default):
        0–25  → Low
        26–50 → Medium
        51–75 → High
        76–100 → Extreme

    Edge cases:
        - NaN/Inf → Extreme (fail-safe)
        - Negative → Low
    """
    if not _is_valid_number(score):
        return RiskLevel.EXTREME  # fail-safe
    if score <= thresholds.low_max:
        return RiskLevel.LOW
    if score <= thresholds.medium_max:
        return RiskLevel.MEDIUM
    if score <= thresholds.high_max:
        return RiskLevel.HIGH
    return RiskLevel.EXTREME


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def score_risk(
    volatility: float,
    max_drawdown: float,
    avg_return: float,
    weights: RiskWeights | None = None,
    thresholds: RiskThresholds | None = None,
) -> RiskResult:
    """Full scoring pipeline: normalize → score → classify.

    This is the main entry point for consumers.

    Args:
        volatility:   Annualised volatility (e.g. 1.5 = 150%).
        max_drawdown: Peak-to-trough decline as ratio (0.0–1.0).
        avg_return:   Average period return (e.g. 0.05 = 5%).
        weights:      Override weights (default: read from app settings).
        thresholds:   Override thresholds (default: 25/50/75 boundaries).

    Returns:
        RiskResult with score, level, and normalized feature values.
    """
    from app.services.risk_engine.risk_config import get_risk_weights

    w = weights or get_risk_weights()
    t = thresholds or DEFAULT_THRESHOLDS

    risk_score = compute_risk_score(volatility, max_drawdown, avg_return, w)
    risk_level = classify_risk_level(risk_score, t)

    return RiskResult(
        risk_score=round(risk_score, 2),
        risk_level=risk_level,
        normalized_volatility=round(normalize_volatility(volatility), 4),
        normalized_drawdown=round(normalize_drawdown(max_drawdown), 4),
        normalized_return=round(normalize_return(avg_return), 4),
    )
