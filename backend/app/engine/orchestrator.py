"""Orchestrator conversacional — roteia intenção e explica, sem gerar números.

Interpreta a pergunta do agricultor, escolhe qual serviço determinístico chamar e
verbaliza o resultado. O LLM (quando há chave) só faz roteamento/explicação; todos
os números vêm dos domain services (ADR-0002, ADR-0010).

Roteamento determinístico (offline, testável) é o padrão; um roteador via Claude é
opcional e cai no determinístico em qualquer falha.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from enum import Enum

from app.services.planting_date import PlantingDateService
from app.services.regional_intelligence import (
    MunicipalityNotInRegion,
    RegionalIntelligenceService,
)

DEFAULT_SEASON = "2026/27"

_MONTHS = {
    "jan": 1, "fev": 2, "mar": 3, "abr": 4, "mai": 5, "jun": 6,
    "jul": 7, "ago": 8, "set": 9, "out": 10, "nov": 11, "dez": 12,
}


class Intent(str, Enum):
    REGIONAL = "regional_intelligence"
    SIMULATION = "planting_simulation"
    OPTIMIZATION = "planting_optimization"
    UNKNOWN = "unknown"


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


@dataclass
class Routed:
    intent: Intent
    municipality: str | None
    season: str
    planting_date: str | None


class DeterministicRouter:
    """Extrai intenção e slots por regras — base do orchestrator."""

    def __init__(self, known_municipalities: list[str]) -> None:
        # mapa nome_normalizado -> canônico, ordenado por tamanho (match mais específico)
        self._munis = sorted(known_municipalities, key=len, reverse=True)

    def _municipality(self, text: str) -> str | None:
        n = _norm(text)
        for name in self._munis:
            if _norm(name) in n:
                return name
        return None

    def _season(self, text: str) -> str:
        m = re.search(r"\b(20\d{2})\s*/\s*(\d{2})\b", text)
        return f"{m.group(1)}/{m.group(2)}" if m else DEFAULT_SEASON

    def _planting_date(self, text: str, harvest_year: int) -> str | None:
        n = _norm(text)
        plant_year = harvest_year - 1
        # "20 de outubro", "20 out"
        m = re.search(r"\b(\d{1,2})\s*(?:de\s*)?([a-z]{3,9})\b", n)
        if m and m.group(2)[:3] in _MONTHS:
            day, month = int(m.group(1)), _MONTHS[m.group(2)[:3]]
            return _safe_date(plant_year, month, day)
        # "20/10" ou "20-10"
        m = re.search(r"\b(\d{1,2})[/-](\d{1,2})\b", text)
        if m:
            return _safe_date(plant_year, int(m.group(2)), int(m.group(1)))
        # "em novembro" (sem dia) -> dia 1
        for key, month in _MONTHS.items():
            if re.search(rf"\bem\s+{key}", n):
                return _safe_date(plant_year, month, 1)
        return None

    def route(self, message: str, ctx_municipality: str | None) -> Routed:
        n = _norm(message)
        season = self._season(message)
        harvest_year = int(season.split("/")[0]) + 1
        muni = self._municipality(message) or ctx_municipality
        planting = self._planting_date(message, harvest_year)

        if re.search(r"melhor\s+(data|epoca|periodo)|qual\s+data|quando\s+plant|otimiz", n):
            intent = Intent.OPTIMIZATION
        elif planting and re.search(r"vale|se\s+eu\s+plant|plantar\s+em|colheria|e\s+se", n):
            intent = Intent.SIMULATION
        elif re.search(r"risco|quanto|produtiv|colher|colheria|safra|expectativa", n):
            intent = Intent.REGIONAL if not planting else Intent.SIMULATION
        else:
            intent = Intent.UNKNOWN
        return Routed(intent, muni, season, planting)


@dataclass
class Orchestrator:
    regional: RegionalIntelligenceService
    planting: PlantingDateService
    router: DeterministicRouter

    def handle(self, message: str, ctx_municipality: str | None = None) -> dict:
        r = self.router.route(message, ctx_municipality)
        if r.municipality is None:
            return self._reply(r, None, "Para responder, preciso do município (ex.: Horizontina).")
        try:
            return self._dispatch(r)
        except MunicipalityNotInRegion:
            return self._reply(
                r, None,
                f"O município '{r.municipality}' está fora da região coberta pelo MVP "
                "(microrregião Três Passos/RS).",
            )

    def _dispatch(self, r: Routed) -> dict:
        if r.intent == Intent.OPTIMIZATION:
            res = self.planting.optimize(r.municipality, "soja", r.season)
            best = res["top_recommendations"][0]
            answer = (
                f"A data mais robusta para soja em {res['municipality']} na safra "
                f"{r.season} é {best['planting_date']}: produtividade esperada "
                f"{best['expected_yield_sc_ha']} sc/ha, piso {best['downside_sc_ha']} sc/ha "
                f"(P10). {best['justification']}"
            )
            return self._reply(r, res, answer)
        if r.intent == Intent.SIMULATION:
            res = self.planting.simulate(r.municipality, "soja", r.season, r.planting_date)
            answer = (
                f"Plantando em {res['evaluated_planting_date']} em {res['municipality']}: "
                f"produtividade esperada {res['expected_yield_sc_ha']} sc/ha "
                f"({res['delta_vs_baseline_sc_ha']:+} vs data-base), piso "
                f"{res['downside_sc_ha']} sc/ha. {res['explanation']}"
            )
            return self._reply(r, res, answer)
        if r.intent == Intent.REGIONAL:
            res = self.regional.run(r.municipality, "soja", r.season)
            return self._reply(r, res, res["explanation"])
        return self._reply(
            r, None,
            "Posso estimar produtividade regional, simular uma data de plantio ou "
            "recomendar a melhor janela. Reformule, por favor (ex.: 'qual a melhor data "
            "para plantar soja em Horizontina?').",
        )

    @staticmethod
    def _reply(r: Routed, result: dict | None, answer: str) -> dict:
        return {
            "intent": r.intent.value,
            "parameters": {
                "municipality": r.municipality,
                "season": r.season,
                "planting_date": r.planting_date,
            },
            "result": result,
            "answer": answer,
        }


def _safe_date(year: int, month: int, day: int) -> str | None:
    try:
        return date(year, month, day).isoformat()
    except ValueError:
        return None
