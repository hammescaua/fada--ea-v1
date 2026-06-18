"""Endpoint do dashboard da fazenda (/home)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.routes.regional_intelligence import _model
from app.infra.db import get_session
from app.infra.repositories import EventRepository, FarmRepository, PlanningRepository
from app.services.dashboard import DashboardService, FarmNotFound
from app.services.decisions import DecisionsService
from app.services.insights import InsightsService
from app.services.planning import PlanningService

router = APIRouter()


def get_service(session: Session = Depends(get_session)) -> DashboardService:
    try:
        model = _model()
    except FileNotFoundError as exc:
        raise HTTPException(503, "Modelo ausente.") from exc
    farms = FarmRepository(session)
    events = EventRepository(session)
    planning = PlanningRepository(session)
    insights = InsightsService(farms=farms, events=events, model=model)
    return DashboardService(
        farms=farms,
        decisions=DecisionsService(farms=farms, events=events, planning=planning,
                                   model=model, insights=insights),
        planning=PlanningService(farms=farms, planning=planning, events=events),
        insights=insights,
    )


@router.get("/farms/{farm_id}/dashboard")
def dashboard(farm_id: int, svc: DashboardService = Depends(get_service)) -> dict:
    try:
        return svc.farm_dashboard(farm_id)
    except FarmNotFound as exc:
        raise HTTPException(404, f"Farm {exc} inexistente") from exc
