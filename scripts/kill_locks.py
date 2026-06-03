import sys
from app.core.db import engine
from sqlalchemy import text

if __name__ == "__main__":
    with engine.connect() as conn:
        res = conn.execute(text("SELECT pid, wait_event_type, wait_event, state, query FROM pg_stat_activity WHERE state != 'idle'"))
        for row in res:
            print(dict(row._mapping))
        
        # Kill transactions that have been running for a long time
        cancel_q = text("""
            SELECT pg_terminate_backend(pid) 
            FROM pg_stat_activity 
            WHERE state = 'active'
              AND wait_event_type = 'Lock'
              OR (state = 'idle in transaction' AND state_change < now() - INTERVAL '1 minute');
        """)
        conn.execute(cancel_q)
        conn.commit()
        print("Cleared stale connections.")
