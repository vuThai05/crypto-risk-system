#!/usr/bin/env python3
"""Run the background scheduler (market, OHLCV, weekly backfill).

Usage::

    uv run python scripts/run_worker.py

Requires ``.env`` with valid ``POSTGRES_*`` (e.g. Supabase).
"""

from __future__ import annotations

from app.worker.scheduler import main

if __name__ == "__main__":
    main()
