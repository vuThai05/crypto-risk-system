# 03_API.md

Use this prompt to design the frontend API contract for Phase 1. This file intentionally focuses on API shape and data behavior, not visual design.

## Prompt

You are a senior full-stack engineer defining the frontend API needs for the Crypto Risk System Phase 1 UI.

Project context:
- The backend is FastAPI with prefix `/api/v1`.
- Current endpoints are useful but too narrow for the Phase 1 UI:
  - `GET /market-risk`
  - `GET /top-risky-assets?limit=...`
  - `GET /coins/{coin_id}/risk`
  - `POST /trigger-ingestion`
- Current models include:
  - `Coin`: `id`, `coingecko_id`, `symbol`, `name`, `market_cap_rank`, `image_url`
  - `MarketSnapshot`: `price_usd`, `market_cap`, `volume_24h`, `percent_change_1h`, `percent_change_24h`, `percent_change_7d`, `timestamp`
  - `FeatureMetric`: `volatility`, `drawdown`, `avg_return`, `window`, `computed_at`
  - `RiskMetric`: `risk_score`, `risk_level`, `model_version`, `config_hash`, `computed_at`
  - `MarketAggregate`: `avg_risk_score`, `high_risk_count`, `extreme_risk_count`, `breadth_ratio`, `market_volatility`, `btc_dominance`, `timestamp`
- Phase 1 UI needs a bubble risk map, a coin risk dossier, market weather, and data trust/ops.
- The frontend must never call CoinGecko directly.

## Existing Endpoints To Reuse

Use existing endpoints when possible:

```txt
GET  /api/v1/market-risk
GET  /api/v1/top-risky-assets?limit=10
GET  /api/v1/coins/{coin_id}/risk
POST /api/v1/trigger-ingestion
```

## Required Backend Additions For Phase 1

Define these API contracts before building the frontend against mock data.

### `GET /api/v1/risk-map`

Purpose:
- Fetch the full top-100 bubble map in one request.
- This should replace the need for the frontend to call `top-risky-assets` repeatedly.

Query params:
- `limit`: default `100`, min `1`, max `100`

Response shape:

```json
{
  "data": [
    {
      "coin_id": "uuid",
      "coingecko_id": "bitcoin",
      "symbol": "btc",
      "name": "Bitcoin",
      "image_url": "https://...",
      "market_cap_rank": 1,
      "price_usd": 65000.12,
      "market_cap": 1280000000000,
      "volume_24h": 32000000000,
      "percent_change_1h": -0.3,
      "percent_change_24h": 2.1,
      "percent_change_7d": 4.8,
      "risk_score": 42.5,
      "risk_level": "Medium",
      "risk_computed_at": "2026-04-14T10:15:00Z",
      "market_timestamp": "2026-04-14T10:15:00Z"
    }
  ],
  "count": 100,
  "generated_at": "2026-04-14T10:16:00Z",
  "freshness": {
    "is_stale": false,
    "lag_seconds": 60,
    "status": "fresh"
  }
}
```

### `GET /api/v1/market-weather`

Purpose:
- Fetch the market-level risk briefing used by the top strip and insight rail.

Response shape:

```json
{
  "avg_risk_score": 47.2,
  "risk_state": "Choppy",
  "high_risk_count": 18,
  "extreme_risk_count": 3,
  "breadth_ratio": 0.43,
  "market_volatility": 1.25,
  "btc_dominance": 52.1,
  "timestamp": "2026-04-14T10:15:00Z",
  "freshness": {
    "is_stale": false,
    "lag_seconds": 60,
    "status": "fresh"
  }
}
```

Allowed `risk_state` values:
- `Calm`
- `Choppy`
- `Stress`
- `Panic`
- `Unknown`

### `GET /api/v1/coins/{coin_id}/risk-dossier`

Purpose:
- Fetch everything needed for the coin drill-down panel/page in one request.

Response shape:

```json
{
  "coin": {
    "id": "uuid",
    "coingecko_id": "bitcoin",
    "symbol": "btc",
    "name": "Bitcoin",
    "market_cap_rank": 1,
    "image_url": "https://..."
  },
  "market": {
    "price_usd": 65000.12,
    "market_cap": 1280000000000,
    "volume_24h": 32000000000,
    "percent_change_1h": -0.3,
    "percent_change_24h": 2.1,
    "percent_change_7d": 4.8,
    "timestamp": "2026-04-14T10:15:00Z"
  },
  "risk": {
    "risk_score": 42.5,
    "risk_level": "Medium",
    "model_version": "1.0.0",
    "config_hash": "abc123",
    "computed_at": "2026-04-14T10:15:00Z"
  },
  "features": [
    {
      "window": "7d",
      "volatility": 1.18,
      "drawdown": 0.21,
      "avg_return": -0.02,
      "computed_at": "2026-04-14T10:15:00Z"
    }
  ],
  "freshness": {
    "is_stale": false,
    "lag_seconds": 60,
    "status": "fresh"
  }
}
```

### `GET /api/v1/system/data-freshness`

Purpose:
- Help the UI tell the user whether the displayed risk data is trustworthy.

Response shape:

```json
{
  "market_snapshot_latest_at": "2026-04-14T10:15:00Z",
  "risk_metric_latest_at": "2026-04-14T10:15:00Z",
  "market_aggregate_latest_at": "2026-04-14T10:15:00Z",
  "lag_seconds": 60,
  "is_stale": false,
  "status": "fresh",
  "warnings": []
}
```

Allowed `status` values:
- `fresh`
- `lagging`
- `stale`
- `empty`
- `error`

## Frontend API Client Rules

- Build a typed client in `src/api/`.
- Normalize number-like values from `number | string | null` into `number | null`.
- Normalize date fields into ISO strings at the API boundary. Components can format dates later.
- Convert FastAPI `{ "detail": "..." }` errors into a shared frontend error type.
- Keep polling conservative. Backend reads are cheap, but Phase 1 should not create noisy refresh behavior.
- `POST /trigger-ingestion` must invalidate `risk-map`, `market-weather`, `coin-dossier`, and `data-freshness` queries after success.

## Output Required From The Agent

When this prompt is used, output:
- The exact TypeScript API types.
- The typed frontend fetch functions.
- The query/mutation names that will be consumed by TanStack Query.
- Any backend routes that must be implemented before removing mocks.
- A short migration path from current endpoints to Phase 1 endpoints.

## Acceptance Criteria

- The bubble map can load in one API request.
- The coin dossier can load in one API request.
- Freshness is first-class in every user-facing risk surface.
- The frontend does not need to understand database table structure.
- The frontend does not call CoinGecko.
