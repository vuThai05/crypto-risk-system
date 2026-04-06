"""API router aggregation — registers all route modules.

Follows the pattern from full-stack-fastapi-template/backend/app/api/main.py.
"""

from fastapi import APIRouter

from app.api.routes import coin_risk, health, ingestion, market_risk, top_risky

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(market_risk.router)
api_router.include_router(coin_risk.router)
api_router.include_router(top_risky.router)
api_router.include_router(ingestion.router)
