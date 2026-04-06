"""FastAPI application entry point.

Follows the pattern from full-stack-fastapi-template/backend/app/main.py:
    - App factory with CORS middleware
    - Lifespan context for startup/shutdown hooks
    - Router mounting under API_V1_STR prefix

Background ingestion runs in a **separate worker process** (``scripts/run_worker.py``),
not inside this app — see ``prompts/dbstructure.md``.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings
from app.core.db import init_db_if_enabled
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle.

    On startup:
        1. Configure structured logging
        2. Initialise database tables (dev convenience)
    """
    setup_logging(
        log_level="DEBUG" if settings.ENVIRONMENT == "local" else "INFO",
        json_output=settings.ENVIRONMENT != "local",
    )

    init_db_if_enabled()

    yield


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS
if settings.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)
