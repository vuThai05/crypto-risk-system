"""Database engine and session factory.

Follows the pattern from full-stack-fastapi-template/backend/app/core/db.py.
"""

from __future__ import annotations

from time import sleep

import structlog
from sqlalchemy import text
from sqlalchemy.exc import InterfaceError, OperationalError
from sqlmodel import Session, create_engine

from app.core.config import settings

logger = structlog.get_logger()

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    connect_args={"connect_timeout": 15},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300,
)


def init_db() -> None:
    """Create all tables from metadata.

    Use this explicitly from setup scripts/migrations. Do not call unconditionally
    on production startup.
    """
    from sqlmodel import SQLModel  # noqa: F811

    # Ensure all models are imported so metadata is populated
    import app.models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def init_db_if_enabled() -> None:
    """Create tables only when AUTO_CREATE_TABLES=true.

    This keeps Supabase/prod startup safe while still allowing local bootstrap.
    """
    if not settings.AUTO_CREATE_TABLES:
        logger.info("db_auto_create_skipped", auto_create_tables=False)
        return
    logger.warning("db_auto_create_enabled", auto_create_tables=True)
    init_db()


def wait_for_db_connection(*, attempts: int = 3, delay_seconds: float = 2.0) -> None:
    """Verify DB connectivity before jobs start mutating data.

    GitHub Actions jobs can occasionally hit transient pooler/SSL EOF errors on
    the first checkout. A short preflight retry keeps those from failing a whole
    scheduled run while still surfacing persistent secret/config issues.
    """
    for attempt in range(1, attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            if attempt > 1:
                logger.info("db_connection_ready", attempt=attempt)
            return
        except (InterfaceError, OperationalError) as exc:
            engine.dispose()
            if attempt >= attempts:
                logger.error(
                    "db_connection_check_failed",
                    attempt=attempt,
                    attempts=attempts,
                    error=str(exc),
                )
                raise

            wait_seconds = delay_seconds * attempt
            logger.warning(
                "db_connection_check_retry",
                attempt=attempt,
                attempts=attempts,
                wait_seconds=wait_seconds,
                error=str(exc),
            )
            sleep(wait_seconds)


def get_session():
    """Yield a DB session — used as a FastAPI dependency."""
    with Session(engine) as session:
        yield session
