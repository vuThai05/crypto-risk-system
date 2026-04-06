"""Unit tests for the feature engineering module.

Tests pure functions — no database or network required.
"""

from app.services.feature_engineering.feature_service import (
    compute_avg_return,
    compute_features,
    compute_max_drawdown,
    compute_volatility,
)


# ── compute_volatility ────────────────────────────────────────────────────

class TestComputeVolatility:
    def test_empty_list(self):
        assert compute_volatility([]) == 0.0

    def test_single_price(self):
        assert compute_volatility([100.0]) == 0.0

    def test_constant_prices(self):
        """Zero volatility when prices don't change."""
        assert compute_volatility([100.0, 100.0, 100.0, 100.0]) == 0.0

    def test_positive_volatility(self):
        """Varying prices should produce positive volatility."""
        prices = [100.0, 105.0, 95.0, 110.0, 90.0, 115.0]
        vol = compute_volatility(prices)
        assert vol > 0.0

    def test_higher_variance_means_higher_vol(self):
        """More volatile series should have higher volatility."""
        stable = [100.0, 101.0, 99.0, 100.5, 99.5]
        wild = [100.0, 150.0, 50.0, 200.0, 30.0]
        assert compute_volatility(wild) > compute_volatility(stable)


# ── compute_max_drawdown ──────────────────────────────────────────────────

class TestComputeMaxDrawdown:
    def test_empty_list(self):
        assert compute_max_drawdown([]) == 0.0

    def test_single_price(self):
        assert compute_max_drawdown([100.0]) == 0.0

    def test_monotonically_increasing(self):
        """No drawdown when prices only go up."""
        assert compute_max_drawdown([100.0, 110.0, 120.0, 130.0]) == 0.0

    def test_50_percent_drawdown(self):
        """Peak 200 → trough 100 = 50% drawdown."""
        prices = [100.0, 200.0, 100.0]
        dd = compute_max_drawdown(prices)
        assert abs(dd - 0.5) < 0.001

    def test_full_drawdown(self):
        """100 → 0 should be 100% drawdown (value 1.0)."""
        prices = [100.0, 50.0, 0.0]
        dd = compute_max_drawdown(prices)
        assert abs(dd - 1.0) < 0.001


# ── compute_avg_return ────────────────────────────────────────────────────

class TestComputeAvgReturn:
    def test_empty_list(self):
        assert compute_avg_return([]) == 0.0

    def test_single_price(self):
        assert compute_avg_return([100.0]) == 0.0

    def test_positive_return(self):
        """100 → 110 = 10% return."""
        ret = compute_avg_return([100.0, 110.0])
        assert abs(ret - 0.10) < 0.001

    def test_negative_return(self):
        """100 → 90 = −10% return."""
        ret = compute_avg_return([100.0, 90.0])
        assert abs(ret - (-0.10)) < 0.001

    def test_mixed_returns(self):
        """Average of +10% and −10%."""
        ret = compute_avg_return([100.0, 110.0, 99.0])
        assert isinstance(ret, float)


# ── compute_features ──────────────────────────────────────────────────────

class TestComputeFeatures:
    def test_insufficient_data(self):
        assert compute_features([]) is None
        assert compute_features([100.0]) is None

    def test_returns_features(self):
        prices = [100.0, 105.0, 95.0, 110.0, 90.0]
        features = compute_features(prices)
        assert features is not None
        assert features.volatility > 0.0
        assert 0.0 <= features.max_drawdown <= 1.0
        assert isinstance(features.avg_return, float)
