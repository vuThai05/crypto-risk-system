"""Application settings — loaded from environment variables via pydantic-settings.

Follows the pattern from full-stack-fastapi-template/backend/app/core/config.py.
"""

from __future__ import annotations

import secrets
import warnings
from typing import Annotated, Any, Literal

from pydantic import AnyUrl, BeforeValidator, HttpUrl, PostgresDsn, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse_cors(v: Any) -> list[str] | str:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, list | str):
        return v
    raise ValueError(v)


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # ── App ────────────────────────────────────────────────────────────────
    PROJECT_NAME: str = "Crypto Risk System"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    BACKEND_CORS_ORIGINS: Annotated[
        list[AnyUrl] | str, BeforeValidator(parse_cors)
    ] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def all_cors_origins(self) -> list[str]:
        return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]

    # ── PostgreSQL ─────────────────────────────────────────────────────────
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = "crypto_risk"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        return PostgresDsn.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )

    # ── CoinGecko ──────────────────────────────────────────────────────────
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    COINGECKO_API_KEY: str | None = None
    COINGECKO_MAX_REQUESTS_PER_MINUTE: int = 25

    # ── Risk Engine Weights ────────────────────────────────────────────────
    RISK_WEIGHT_VOLATILITY: float = 0.40
    RISK_WEIGHT_DRAWDOWN: float = 0.35
    RISK_WEIGHT_RETURN: float = 0.25

    # ── Scheduler / worker intervals ───────────────────────────────────────
    INGESTION_INTERVAL_MINUTES: int = 15
    OHLCV_INTERVAL_HOURS: int = 12
    BACKFILL_INTERVAL_DAYS: int = 7
    RISK_MODEL_VERSION: str = "1.0.0"
    AUTO_CREATE_TABLES: bool = False

    # ── Sentry (optional) ─────────────────────────────────────────────────
    SENTRY_DSN: HttpUrl | None = None

    # ── Safety checks ─────────────────────────────────────────────────────

    def _check_default_secret(self, var_name: str, value: str | None) -> None:
        if value == "changethis":
            message = (
                f'The value of {var_name} is "changethis", '
                "for security, please change it, at least for deployments."
            )
            if self.ENVIRONMENT == "local":
                warnings.warn(message, stacklevel=1)
            else:
                raise ValueError(message)

    @model_validator(mode="after")
    def _enforce_non_default_secrets(self) -> Self:
        self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
        self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
        return self


settings = Settings()  # type: ignore
