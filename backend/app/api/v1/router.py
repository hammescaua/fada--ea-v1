"""Roteador agregador da API v1."""

from fastapi import APIRouter

from app.api.v1.routes import health, regional_intelligence

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(regional_intelligence.router, tags=["regional-intelligence"])
