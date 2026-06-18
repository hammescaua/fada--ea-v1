"""Endpoint de status do sistema."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infra.db import get_session
from app.services.system import system_status

router = APIRouter()


@router.get("/system/status")
def status(session: Session = Depends(get_session)) -> dict:
    return system_status(session)
