We are refactoring a crypto market ingestion system to make it production-ready.

IMPORTANT:

* This is a REFACTOR task (NOT rewrite from scratch)
* Keep existing architecture and naming unless necessary
* Focus on performance, correctness, and clean transaction handling

---

CONTEXT:

Current ingestion flow:
fetch → validate → upsert coins → insert prices

Problems identified:

1. coin_repository:

   * upsert_coins() calls upsert_coin() in a loop
   * each coin triggers its own COMMIT
   * result: 100 coins = 100 commits (inefficient)

2. ingestion_service:

   * does not control transaction
   * repositories commit independently
   * risk of partial writes (inconsistent DB state)

3. price_repository:

   * already uses bulk insert with ON CONFLICT DO NOTHING
   * but should align with global transaction strategy

---

YOUR TASK:

### PART 1 — OPTIMIZE coin_repository (CRITICAL)

Refactor coin_repository to:

1. Implement a new function:
   bulk_upsert_coins(session, coins_in)

2. Requirements:

   * Use PostgreSQL:
     INSERT ... ON CONFLICT (coingecko_id) DO UPDATE
   * Perform bulk operation (NOT loop)
   * NO session.commit() inside this function
   * Return list of upserted Coin objects

3. Remove per-coin commit behavior

---

### PART 2 — FIX TRANSACTION HANDLING (ingestion_service)

Refactor ingestion_service.run_ingestion():

1. Enforce a single transaction boundary:

   * NO commits inside repositories
   * Commit ONLY once at the end

2. Add:

   try:
   ...
   session.commit()
   except Exception:
   session.rollback()
   raise

3. Ensure:

   * coin upsert + price insert happen atomically
   * no partial data if failure occurs

---

### PART 3 — ALIGN price_repository

1. Remove internal commit from insert_prices()

2. Keep:

   * ON CONFLICT DO NOTHING
   * bulk insert behavior

3. Let ingestion_service handle commit

---

CONSTRAINTS:

* Do NOT introduce new frameworks (no Celery, no async DB rewrite)
* Stay consistent with SQLModel + SQLAlchemy
* Keep function signatures clean and testable
* Maintain idempotency

---

OUTPUT:

1. Updated coin_repository.py
2. Updated ingestion_service.py
3. Updated price_repository.py
4. Short explanation of:

   * how transaction flow works now
   * why performance is improved

---

IMPORTANT:

* Avoid unnecessary abstraction
* Focus on correctness + performance
* Think like a production backend engineer, not a tutorial writer