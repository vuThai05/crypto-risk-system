"""API dependencies — session injection following the template pattern."""

from __future__ import annotations

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.core.db import engine


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for the request lifecycle."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
