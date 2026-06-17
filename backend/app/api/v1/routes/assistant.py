"""Endpoint conversacional /assistant."""

from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException

from app.api.v1.routes.planting_date import _service as _planting_service
from app.api.v1.routes.regional_intelligence import _model
from app.engine import build_explainer
from app.engine.orchestrator import DeterministicRouter, Orchestrator
from app.schemas.assistant import AssistantRequest, AssistantResponse
from app.services.regional_intelligence import RegionalIntelligenceService

router = APIRouter()


@lru_cache
def _orchestrator() -> Orchestrator:
    model = _model()
    names = [info["name"] for info in model.municipalities().values()]
    return Orchestrator(
        regional=RegionalIntelligenceService(model=model, explainer=build_explainer()),
        planting=_planting_service(),
        router=DeterministicRouter(known_municipalities=names),
    )


def get_orchestrator() -> Orchestrator:
    try:
        return _orchestrator()
    except FileNotFoundError as exc:
        raise HTTPException(503, "Modelo/grid ausente.") from exc


@router.post("/assistant", response_model=AssistantResponse)
def assistant(
    body: AssistantRequest, orch: Orchestrator = Depends(get_orchestrator)
) -> AssistantResponse:
    return AssistantResponse(**orch.handle(body.message, ctx_municipality=body.municipality))
