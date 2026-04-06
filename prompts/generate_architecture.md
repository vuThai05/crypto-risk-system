@fastapi/full-stack-fastapi-template
@antigravity-awesome-skills/backend_patterns.md
@antigravity-awesome-skills/system_design.md

/plan /design

Build a crypto market risk analytics backend system (python) using a modular monolith architecture.

GOAL:

* Analyze crypto market risk (NOT price prediction)
* Focus on Top 100 cryptocurrencies
* Convert raw price data into risk signals
* Provide APIs for future dashboard
* System should be easy to extend to cloud in the future (but DO NOT implement cloud now)


STRICT REQUIREMENTS:

1. MUST reuse structure and conventions from full-stack-fastapi-template:

   * app/api
   * app/crud (or repositories)
   * app/core
   *   app/utils
   * dependency injection
   * config handling

2. MUST follow backend best practices from awesome-skills:

   * clean architecture
   * separation of concerns
   * testability
   * no business logic inside API layer

ARCHITECTURE:

* Modular monolith (NOT microservices)

LAYERS:

1. ingestion module
2. feature_engineering module
3. risk_engine module (CORE)
4. repository layer (DB access)
5. API layer (FastAPI)
6. background worker

DATABASE:

* PostgreSQL
* Design tables:

  * coins
  * price_history (time-series)
  * risk_metrics
  * market_snapshots

API:

* GET /market-risk
* GET /coins/{id}/risk
* GET /top-risky-assets

BACKGROUND JOB:

* periodic data ingestion
* periodic risk computation

OUTPUT:

* full project structure (aligned with template)
* database schema
* module responsibilities
* data flow