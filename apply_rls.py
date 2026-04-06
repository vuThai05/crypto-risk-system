"""Apply Row Level Security policies to all Supabase tables.

Usage:  python apply_rls.py
"""

import sys
import logging

from sqlmodel import Session, text

from app.core.db import engine, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Actual table names from SQLModel __tablename__ definitions
TABLES = [
    "coins",
    "market_snapshots",
    "ohlcv_candles",
    "feature_metrics",
    "risk_metrics",
    "market_aggregates",
]


def apply_rls() -> None:
    # Step 1 — ensure all tables exist
    logger.info("Initializing database tables (if they don't exist)...")
    init_db()

    # Step 2 — enable RLS + read-only policies
    logger.info("Applying Row Level Security (RLS) policies...")
    try:
        with Session(engine) as session:
            for table in TABLES:
                # Enable RLS
                session.exec(text(f'ALTER TABLE "{table}" ENABLE ROW LEVEL SECURITY;'))
                logger.info(f"  ✓ RLS enabled on [{table}]")

                # Create read-only policy (idempotent via IF NOT EXISTS)
                policy_name = f"Allow public read access to {table}"
                session.exec(text(f"""
                    DO $$
                    BEGIN
                        IF NOT EXISTS (
                            SELECT 1 FROM pg_policies
                            WHERE tablename = '{table}'
                              AND policyname = '{policy_name}'
                        ) THEN
                            EXECUTE format(
                                'CREATE POLICY %I ON {table} FOR SELECT USING (true)',
                                '{policy_name}'
                            );
                        END IF;
                    END $$;
                """))
                logger.info(f"  ✓ SELECT policy on [{table}]")

            session.commit()
            logger.info("All RLS policies applied successfully!")
    except Exception as e:
        logger.error(f"Failed to apply RLS policies: {e}")
        sys.exit(1)


if __name__ == "__main__":
    apply_rls()
