"""Roteador agregador da API v1."""

from fastapi import APIRouter

from app.api.v1.routes import (
    assistant,
    farms,
    health,
    planting_date,
    regional_intelligence,
)

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(regional_intelligence.router, tags=["regional-intelligence"])
api_router.include_router(planting_date.router, tags=["planting-date"])
api_router.include_router(farms.router, tags=["ground-truth"])
api_router.include_router(assistant.router, tags=["assistant"])
