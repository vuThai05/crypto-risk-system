We are migrating an existing FastAPI + PostgreSQL (pgAdmin/local) backend system to Supabase.

IMPORTANT:

* Supabase will be used ONLY as a managed PostgreSQL database
* DO NOT replace backend with supabase-js
* DO NOT rewrite architecture
* Keep repository pattern, SQLModel, and service layers intact

---

CURRENT SYSTEM:

* Backend: FastAPI
* ORM: SQLModel / SQLAlchemy
* Database: PostgreSQL (local via pgAdmin)
* Architecture:
  ingestion → repository → database

---

GOAL:

* Replace local PostgreSQL with Supabase PostgreSQL
* Keep backend logic unchanged
* Ensure production-ready setup

---

### PART 1 — DATABASE MIGRATION

1. Analyze existing schema:

   * tables
   * relationships
   * constraints
   * indexes

2. Generate SQL compatible with Supabase:

   * UUID support (uuid-ossp or gen_random_uuid)
   * timestamps with timezone
   * foreign keys
   * unique constraints

3. Ensure:

   * no breaking changes
   * compatibility with Supabase Postgres

4. Highlight:

   * any unsupported extensions
   * required Supabase configurations

---

### PART 2 — CONNECTION MIGRATION (CRITICAL)

1. Replace DATABASE_URL:

   From:
   postgresql://user:pass@localhost:5432/db

   To:
   Supabase connection string

2. Show how to update:

   * .env file
   * database.py / session config

3. Ensure:

   * connection pooling works
   * SSL mode is enabled (required by Supabase)

---

### PART 3 — KEEP BACKEND ARCHITECTURE

1. DO NOT:

   * replace repository layer
   * remove SQLModel
   * introduce supabase-js in backend

2. Ensure:

   * all repositories still work
   * queries remain SQLAlchemy-based

---

### PART 4 — OPTIONAL (FRONTEND ONLY)

IF frontend exists:

* show how to use supabase-js ONLY for:

  * auth
  * simple reads

Otherwise skip

---

### PART 5 — SECURITY (SUPABASE)

1. Enable Row Level Security (RLS)

2. Define basic policies:

   * SELECT
   * INSERT
   * UPDATE
   * DELETE

3. Ensure:

   * backend (service role) can bypass RLS if needed
   * frontend users are restricted

---

### PART 6 — TESTING

1. Verify:

   * connection works
   * data is readable/writable
   * ingestion pipeline still works

2. Provide:

   * sample SQL queries
   * test API calls

---

### PART 7 — CLEANUP

1. Identify:

   * old local DB configs to remove
   * unnecessary pgAdmin dependencies

2. Suggest:

   * final project structure

---

OUTPUT:

* Updated connection config
* Migration SQL
* Required environment variables
* Step-by-step migration guide
* Explanation of changes

---

IMPORTANT:

* Think like a backend engineer deploying to production
* Avoid unnecessary changes
* Focus on stability, not novelty
