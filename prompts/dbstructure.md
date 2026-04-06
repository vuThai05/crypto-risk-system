Implement the full database schema and data pipeline for a crypto market risk analytics system.

GOAL:

* Build a production-ready data layer for crypto risk analysis
* Focus on Top 100 coins
* Optimize API usage (CoinGecko)
* Support risk computation (volatility, drawdown, risk score)

---

DATABASE REQUIREMENTS:

Use PostgreSQL with SQLAlchemy models.

Design the following tables:

1. coins

* id (UUID, PK)
* coingecko_id (unique)
* symbol
* name
* market_cap_rank
* image_url
* created_at
* updated_at

2. market_snapshots (core ingestion layer)

* id (UUID, PK)
* coin_id (FK)
* price_usd (NUMERIC)
* market_cap (NUMERIC)
* volume_24h (NUMERIC)
* percent_change_1h
* percent_change_24h
* percent_change_7d
* timestamp (indexed)

3. ohlcv_candles (analytics layer)

* id (UUID, PK)
* coin_id (FK)
* timeframe ('12h')
* open_price
* high_price
* low_price
* close_price
* volume
* timestamp
* UNIQUE(coin_id, timeframe, timestamp)

4. feature_metrics

* id
* coin_id
* volatility
* drawdown
* avg_return
* window ('7d', '30d')
* computed_at

5. risk_metrics

* id
* coin_id
* risk_score
* risk_level
* model_version
* config_hash
* computed_at

6. market_aggregates

* id
* avg_risk_score
* high_risk_count
* extreme_risk_count
* breadth_ratio
* market_volatility
* btc_dominance
* timestamp

---

INDEXING & CONSTRAINTS:

* Add index (coin_id, timestamp DESC) for time-series tables
* Use NUMERIC instead of FLOAT for financial data
* Ensure uniqueness where appropriate
* Prepare structure for future partitioning (time-based)

---

DATA PIPELINE REQUIREMENTS:

Implement services:

1. Market Ingestion Service

* Call CoinGecko /coins/markets
* Frequency: every 15 minutes
* Insert into market_snapshots
* Must be idempotent (avoid duplicates)

2. OHLCV Ingestion Service

* Call /coins/{id}/market_chart
* Frequency: every 12 hours
* For Top 100 coins
* Insert into ohlcv_candles

3. Metadata Loader

* Fetch Top 100 coins once at startup
* Insert into coins table
* Do not refetch daily

4. Weekly Backfill Service

* Fetch historical data for each coin
* Run once per week
* Ensure no duplicate inserts

---

SCHEDULER REQUIREMENTS:

Create a separate worker module:

worker/
scheduler.py

Scheduler logic:

* market ingestion → every 15 minutes
* ohlcv ingestion → every 12 hours
* weekly backfill → every 7 days

DO NOT run scheduler inside FastAPI app.

---

REPOSITORY LAYER:

* Implement repository pattern for DB access
* No raw SQL inside services
* Use dependency injection from template

---

ERROR HANDLING:

* Retry API calls (max 3 times)
* Exponential backoff
* Log failures

---

OUTPUT:

1. Full SQLAlchemy models
2. Repository classes
3. Ingestion services
4. Scheduler implementation
5. Example run script
6. Explanation of data flow

IMPORTANT:

* Follow structure of full-stack-fastapi-template
* Keep code clean and modular
* No business logic in API layer
* Optimize for maintainability and extensibility

---

OPTIONAL (if possible):

* Add basic logging
* Add simple unit test for ingestion logic