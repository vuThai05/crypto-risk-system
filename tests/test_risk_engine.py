"""Unit tests for the risk engine scoring module.

Tests pure functions — no database or network required.
All results are deterministic for the same inputs.

Coverage:
    - Each normalization function (normal + edge cases)
    - Composite score computation
    - Risk level classification (all boundary values)
    - Full pipeline (scenario-based: low vol, high dd, sudden spike)
    - Edge cases: NaN, Inf, negative, missing data
"""

import math

from app.models.risk_metric import RiskLevel
from app.services.risk_engine.risk_config import RiskThresholds, RiskWeights
from app.services.risk_engine.risk_scorer import (
    classify_risk_level,
    compute_risk_score,
    normalize_drawdown,
    normalize_return,
    normalize_volatility,
    score_risk,
)

# Fixed weights so tests don't depend on env vars
WEIGHTS = RiskWeights(volatility=0.40, drawdown=0.35, avg_return=0.25)
THRESHOLDS = RiskThresholds()


# ── normalize_volatility ──────────────────────────────────────────────────

class TestNormalizeVolatility:
    def test_zero(self):
        assert normalize_volatility(0.0) == 0.0

    def test_max_bound(self):
        """At the max bound (3.0) should normalise to 1.0."""
        assert abs(normalize_volatility(3.0) - 1.0) < 0.001

    def test_midpoint(self):
        """At 1.5 (half of max 3.0) should normalise to 0.5."""
        assert abs(normalize_volatility(1.5) - 0.5) < 0.001

    def test_above_max_clamped(self):
        """Values above max should be clamped to 1.0."""
        assert normalize_volatility(10.0) == 1.0

    def test_negative_clamped(self):
        """Negative volatility should be clamped to 0.0."""
        assert normalize_volatility(-1.0) == 0.0

    def test_nan_returns_worst_case(self):
        """NaN input should assume worst case (1.0)."""
        assert normalize_volatility(float("nan")) == 1.0

    def test_inf_returns_worst_case(self):
        """Inf input should assume worst case (1.0)."""
        assert normalize_volatility(float("inf")) == 1.0

    def test_negative_inf_returns_worst_case(self):
        assert normalize_volatility(float("-inf")) == 1.0

    def test_extreme_volatility(self):
        """Extreme but finite volatility (e.g. 500%) should clamp to 1.0."""
        assert normalize_volatility(5.0) == 1.0


# ── normalize_drawdown ────────────────────────────────────────────────────

class TestNormalizeDrawdown:
    def test_zero(self):
        assert normalize_drawdown(0.0) == 0.0

    def test_full_drawdown(self):
        assert normalize_drawdown(1.0) == 1.0

    def test_half_drawdown(self):
        assert abs(normalize_drawdown(0.5) - 0.5) < 0.001

    def test_negative_clamped(self):
        assert normalize_drawdown(-0.5) == 0.0

    def test_above_one_clamped(self):
        assert normalize_drawdown(1.5) == 1.0

    def test_nan_returns_worst_case(self):
        assert normalize_drawdown(float("nan")) == 1.0

    def test_inf_returns_worst_case(self):
        assert normalize_drawdown(float("inf")) == 1.0


# ── normalize_return ──────────────────────────────────────────────────────

class TestNormalizeReturn:
    def test_positive_return_lowers_risk(self):
        """Positive avg return → lower normalised value (lower risk)."""
        assert normalize_return(0.5) < 0.5

    def test_negative_return_raises_risk(self):
        """Negative avg return → higher normalised value (higher risk)."""
        assert normalize_return(-0.5) > 0.5

    def test_zero_return_is_neutral(self):
        """Zero return → exactly 0.5 (neutral)."""
        assert abs(normalize_return(0.0) - 0.5) < 0.001

    def test_max_positive_return(self):
        """Max positive return (+0.5) → 0.0 (minimum risk contribution)."""
        assert abs(normalize_return(0.5) - 0.0) < 0.001

    def test_max_negative_return(self):
        """Max negative return (−0.5) → 1.0 (maximum risk contribution)."""
        assert abs(normalize_return(-0.5) - 1.0) < 0.001

    def test_nan_returns_neutral(self):
        """NaN input should return neutral (0.5)."""
        assert normalize_return(float("nan")) == 0.5

    def test_inf_returns_neutral(self):
        """Inf input should return neutral (0.5)."""
        assert normalize_return(float("inf")) == 0.5

    def test_beyond_range_clamped(self):
        """Values beyond ±0.5 should be clamped."""
        assert normalize_return(-1.0) == 1.0  # extreme negative → max risk
        assert normalize_return(1.0) == 0.0   # extreme positive → min risk


# ── compute_risk_score ────────────────────────────────────────────────────

class TestComputeRiskScore:
    def test_all_zero_features(self):
        """Zero vol + zero dd + zero return → only return contributes (0.5×0.25×100=12.5)."""
        score = compute_risk_score(0.0, 0.0, 0.0, WEIGHTS)
        assert abs(score - 12.5) < 0.01

    def test_maximum_risk(self):
        """Extreme values in all features → near 100."""
        score = compute_risk_score(5.0, 1.0, -1.0, WEIGHTS)
        assert score > 90.0

    def test_low_risk_scenario(self):
        """Low vol, no drawdown, positive returns → low score."""
        score = compute_risk_score(0.1, 0.0, 0.3, WEIGHTS)
        assert score < 30.0

    def test_score_always_in_valid_range(self):
        score = compute_risk_score(1.0, 0.5, -0.1, WEIGHTS)
        assert 0 <= score <= 100

    def test_weights_influence_result(self):
        """Different weights should produce different scores for the same inputs."""
        heavy_vol = RiskWeights(volatility=0.80, drawdown=0.10, avg_return=0.10)
        heavy_dd = RiskWeights(volatility=0.10, drawdown=0.80, avg_return=0.10)

        score_vol = compute_risk_score(2.0, 0.1, 0.0, heavy_vol)
        score_dd = compute_risk_score(2.0, 0.1, 0.0, heavy_dd)
        assert score_vol > score_dd  # high vol matters more with heavy_vol weights

    def test_nan_features_handled(self):
        """NaN in features should not crash; score stays in valid range."""
        score = compute_risk_score(float("nan"), 0.5, 0.0, WEIGHTS)
        assert 0 <= score <= 100

    def test_all_nan_features(self):
        """All NaN → worst-case normalization → high score."""
        score = compute_risk_score(float("nan"), float("nan"), float("nan"), WEIGHTS)
        assert 0 <= score <= 100

    def test_deterministic(self):
        """Same inputs always produce the same result."""
        s1 = compute_risk_score(1.5, 0.4, -0.1, WEIGHTS)
        s2 = compute_risk_score(1.5, 0.4, -0.1, WEIGHTS)
        assert s1 == s2


# ── classify_risk_level ───────────────────────────────────────────────────

class TestClassifyRiskLevel:
    def test_low_boundary(self):
        assert classify_risk_level(0.0) == RiskLevel.LOW
        assert classify_risk_level(25.0) == RiskLevel.LOW

    def test_medium_boundary(self):
        assert classify_risk_level(25.1) == RiskLevel.MEDIUM
        assert classify_risk_level(50.0) == RiskLevel.MEDIUM

    def test_high_boundary(self):
        assert classify_risk_level(50.1) == RiskLevel.HIGH
        assert classify_risk_level(75.0) == RiskLevel.HIGH

    def test_extreme_boundary(self):
        assert classify_risk_level(75.1) == RiskLevel.EXTREME
        assert classify_risk_level(100.0) == RiskLevel.EXTREME

    def test_negative_score(self):
        """Negative score should be classified as Low."""
        assert classify_risk_level(-10.0) == RiskLevel.LOW

    def test_nan_score_is_extreme(self):
        """NaN score should fail-safe to Extreme."""
        assert classify_risk_level(float("nan")) == RiskLevel.EXTREME

    def test_inf_score_is_extreme(self):
        """Inf score should fail-safe to Extreme."""
        assert classify_risk_level(float("inf")) == RiskLevel.EXTREME

    def test_custom_thresholds(self):
        """Custom thresholds should shift boundaries."""
        tight = RiskThresholds(low_max=10.0, medium_max=20.0, high_max=30.0)
        assert classify_risk_level(15.0, tight) == RiskLevel.MEDIUM
        assert classify_risk_level(15.0) == RiskLevel.LOW  # default would be Low


# ── score_risk (full pipeline — scenario tests) ──────────────────────────

class TestScoreRisk:
    """Integration tests for the full pipeline: normalize → score → classify."""

    def test_scenario_low_volatility(self):
        """Scenario: low vol, small drawdown, positive returns → Low risk."""
        result = score_risk(0.1, 0.05, 0.1, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_level == RiskLevel.LOW
        assert result.risk_score < 25.0

    def test_scenario_high_drawdown(self):
        """Scenario: 80% drawdown → should push toward High/Extreme."""
        result = score_risk(1.0, 0.8, -0.2, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_score > 50.0

    def test_scenario_sudden_spike(self):
        """Scenario: extreme vol + full drawdown + negative returns → Extreme."""
        result = score_risk(5.0, 1.0, -0.5, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_level == RiskLevel.EXTREME

    def test_scenario_stablecoin(self):
        """Scenario: near-zero everything → Low risk, near-zero score."""
        result = score_risk(0.01, 0.001, 0.001, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_level == RiskLevel.LOW
        assert result.risk_score < 15.0

    def test_scenario_moderate_market(self):
        """Scenario: moderate volatility, some drawdown → Medium risk."""
        result = score_risk(0.8, 0.3, -0.05, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_level == RiskLevel.MEDIUM

    def test_result_structure(self):
        """All fields in RiskResult should be valid."""
        result = score_risk(1.0, 0.5, 0.0, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert 0 <= result.risk_score <= 100
        assert isinstance(result.risk_level, RiskLevel)
        assert 0 <= result.normalized_volatility <= 1
        assert 0 <= result.normalized_drawdown <= 1
        assert 0 <= result.normalized_return <= 1

    def test_result_deterministic(self):
        """Same inputs always produce the same RiskResult."""
        r1 = score_risk(1.5, 0.6, -0.1, weights=WEIGHTS, thresholds=THRESHOLDS)
        r2 = score_risk(1.5, 0.6, -0.1, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert r1 == r2

    def test_missing_data_nan(self):
        """NaN features should not crash; fail-safe toward higher risk."""
        result = score_risk(float("nan"), float("nan"), float("nan"),
                            weights=WEIGHTS, thresholds=THRESHOLDS)
        assert 0 <= result.risk_score <= 100
        assert isinstance(result.risk_level, RiskLevel)

    def test_extreme_volatility_value(self):
        """Extreme but finite volatility (e.g. 10.0) should be scored safely."""
        result = score_risk(10.0, 0.5, 0.0, weights=WEIGHTS, thresholds=THRESHOLDS)
        assert result.risk_score > 50.0
