"""Database engine and session factory.

Follows the pattern from full-stack-fastapi-template/backend/app/core/db.py.
"""

from __future__ import annotations

from sqlmodel import Session, create_engine
import structlog

from app.core.config import settings

logger = structlog.get_logger()

engine = create_engine(
    str(settings.SQLALCHEMY_DATABASE_URI),
    echo=False,
    connect_args={"sslmode": "require"},
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
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


def get_session():
    """Yield a DB session — used as a FastAPI dependency."""
    with Session(engine) as session:
        yield session
