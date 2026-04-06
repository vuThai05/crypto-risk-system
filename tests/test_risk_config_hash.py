"""Config hash helper for reproducible risk_metrics rows."""

from app.services.risk_engine.risk_config import RiskWeights, compute_config_hash


def test_compute_config_hash_stable() -> None:
    w = RiskWeights(volatility=0.4, drawdown=0.35, avg_return=0.25)
    a = compute_config_hash(w)
    b = compute_config_hash(w)
    assert a == b
    assert len(a) == 16
