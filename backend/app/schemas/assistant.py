"""DTOs do endpoint conversacional."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AssistantRequest(BaseModel):
    message: str = Field(..., examples=["Qual a melhor data para plantar soja em Horizontina?"])
    municipality: str | None = Field(
        None, description="Município de contexto, usado quando a pergunta não o cita."
    )


class AssistantResponse(BaseModel):
    intent: str
    parameters: dict[str, Any]
    answer: str
    result: dict[str, Any] | None = None
