"""Endpoints de captura de ground truth (Farm/Field/CropCycle/YieldObservation)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.infra.db import get_session
from app.infra.repositories import FarmRepository
from app.schemas.farm import (
    CropCycleCreate,
    CropCycleOut,
    FarmCreate,
    FarmOut,
    FieldCreate,
    FieldOut,
    YieldObservationCreate,
    YieldObservationOut,
)
from app.services.farm import FarmService

router = APIRouter()


def get_service(session: Session = Depends(get_session)) -> FarmService:
    return FarmService(repo=FarmRepository(session))


def _cycle_out(c) -> CropCycleOut:
    return CropCycleOut(
        id=c.id, field_id=c.field_id, crop=c.crop, season=c.season.label,
        harvest_year=c.season.harvest_year, planting_date=c.planting_date,
        created_at=c.created_at,
    )


@router.post("/farms", response_model=FarmOut, status_code=201)
def create_farm(body: FarmCreate, svc: FarmService = Depends(get_service)) -> FarmOut:
    return FarmOut(**vars(svc.create_farm(body.name, body.municipality_code)))


@router.get("/farms", response_model=list[FarmOut])
def list_farms(svc: FarmService = Depends(get_service)) -> list[FarmOut]:
    return [FarmOut(**vars(f)) for f in svc.list_farms()]


@router.post("/farms/{farm_id}/fields", response_model=FieldOut, status_code=201)
def create_field(
    farm_id: int, body: FieldCreate, svc: FarmService = Depends(get_service)
) -> FieldOut:
    try:
        f = svc.create_field(farm_id, body.name, body.area_ha, body.latitude, body.longitude)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    return FieldOut(**vars(f))


@router.get("/farms/{farm_id}/fields", response_model=list[FieldOut])
def list_fields(farm_id: int, svc: FarmService = Depends(get_service)) -> list[FieldOut]:
    return [FieldOut(**vars(f)) for f in svc.list_fields(farm_id)]


@router.post("/fields/{field_id}/crop-cycles", response_model=CropCycleOut, status_code=201)
def create_cycle(
    field_id: int, body: CropCycleCreate, svc: FarmService = Depends(get_service)
) -> CropCycleOut:
    try:
        c = svc.create_cycle(field_id, body.crop, body.season, body.planting_date)
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    return _cycle_out(c)


@router.post("/yield-observations", response_model=YieldObservationOut, status_code=201)
def create_observation(
    body: YieldObservationCreate, svc: FarmService = Depends(get_service)
) -> YieldObservationOut:
    try:
        o = svc.record_observation(**body.model_dump())
    except LookupError as exc:
        raise HTTPException(404, str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from exc
    return YieldObservationOut(**vars(o))


@router.get("/yield-observations", response_model=list[YieldObservationOut])
def list_observations(svc: FarmService = Depends(get_service)) -> list[YieldObservationOut]:
    return [YieldObservationOut(**vars(o)) for o in svc.list_observations()]
