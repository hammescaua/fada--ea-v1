"""Endpoint da fazenda de demonstração."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.v1.routes.regional_intelligence import _model
from app.infra.db import get_session
from app.infra.repositories import EventRepository, FarmRepository, PlanningRepository
from app.services.demo import DemoService

router = APIRouter()


@router.post("/demo/seed", status_code=201)
def seed_demo(session: Session = Depends(get_session)) -> dict:
    try:
        model = _model()
    except FileNotFoundError as exc:
        raise HTTPException(503, "Modelo ausente.") from exc
    svc = DemoService(
        farms=FarmRepository(session), events=EventRepository(session),
        planning=PlanningRepository(session), model=model,
    )
    return svc.seed()
