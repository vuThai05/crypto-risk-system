"""Risk configuration — weights and thresholds for the scoring model.

All values here can be overridden from environment / config.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class RiskWeights:
    """Weighted contributions for the risk score formula."""

    volatility: float = 0.40
    drawdown: float = 0.35
    avg_return: float = 0.25


@dataclass(frozen=True)
class RiskThresholds:
    """Score boundaries for risk classification."""

    low_max: float = 25.0
    medium_max: float = 50.0
    high_max: float = 75.0
    # Anything above high_max → Extreme


def get_risk_weights() -> RiskWeights:
    """Build weights from application settings."""
    return RiskWeights(
        volatility=settings.RISK_WEIGHT_VOLATILITY,
        drawdown=settings.RISK_WEIGHT_DRAWDOWN,
        avg_return=settings.RISK_WEIGHT_RETURN,
    )


# Default thresholds (currently not config-driven)
DEFAULT_THRESHOLDS = RiskThresholds()


def compute_config_hash(weights: RiskWeights) -> str:
    """Short SHA-256 fingerprint of weights for reproducibility (``risk_metrics.config_hash``)."""
    payload = json.dumps(
        {
            "volatility": weights.volatility,
            "drawdown": weights.drawdown,
            "avg_return": weights.avg_return,
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()[:16]
