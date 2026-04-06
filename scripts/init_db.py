#!/usr/bin/env python3
"""Create all tables from SQLModel metadata (development / first deploy).

Usage::

    uv run python scripts/init_db.py
"""

from __future__ import annotations

from app.core.db import init_db

if __name__ == "__main__":
    init_db()
    print("OK: tables created (if not already present).")
