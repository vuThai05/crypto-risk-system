Implement the data ingestion and pipeline system.

REQUIREMENTS:

1. Data Source:

   * CoinGecko API

2. Use repository pattern for DB access

3. Pipeline flow:
   fetch → validate → store → compute features → compute risk

4. Ensure:

   * no duplicate inserts
   * idempotent operations

5. Background execution:

   * simple scheduler (loop or FastAPI background task)

6. Logging:

   * structured logs
   * error handling

OUTPUT:

* ingestion service
* repository layer
* pipeline orchestration