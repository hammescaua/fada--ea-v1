"""Casos de uso de planejamento: PlannedEvent, plano x realizado e agenda."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.planning import (
    PlannedEvent,
    build_agenda,
    compute_plan_vs_actual,
)
from app.infra.repositories import EventRepository, FarmRepository, PlanningRepository


class CycleNotFound(Exception):
    pass


@dataclass
class PlanningService:
    farms: FarmRepository
    planning: PlanningRepository
    events: EventRepository

    def _cycle_or_raise(self, cycle_id: int):
        cycle = self.farms.get_cycle(cycle_id)
        if cycle is None:
            raise CycleNotFound(cycle_id)
        return cycle

    def _area(self, cycle) -> float | None:
        if cycle.area_ha:
            return cycle.area_ha
        field = self.farms.field_of_cycle(cycle.id)
        return field.area_ha if field else None

    def add_planned_event(self, cycle_id: int, **fields) -> PlannedEvent:
        return self.planning.add_planned(PlannedEvent(crop_cycle_id=cycle_id, **fields))

    def list_planned(self, cycle_id: int) -> list[PlannedEvent]:
        return self.planning.list_by_cycle(cycle_id)

    def plan_vs_actual(self, cycle_id: int) -> dict:
        cycle = self._cycle_or_raise(cycle_id)
        planned = self.planning.list_by_cycle(cycle_id)
        actual = self.events.list_by_cycle(cycle_id)
        pva = compute_plan_vs_actual(
            planned, actual, self._area(cycle),
            cycle.target_yield_sc_ha, cycle.expected_price_per_bag,
        )
        return {**vars(pva), "interpretation": _interpret(pva)}

    def agenda(self, cycle_id: int, today: date | None = None) -> dict:
        self._cycle_or_raise(cycle_id)
        planned = self.planning.list_by_cycle(cycle_id)
        actual = self.events.list_by_cycle(cycle_id)
        items = build_agenda(planned, actual, today or date.today())
        counts = {"concluída": 0, "atrasada": 0, "próxima": 0}
        for i in items:
            counts[i.status] += 1
        return {
            "crop_cycle_id": cycle_id,
            "items": [vars(i) for i in items],
            "summary": counts,
        }


def _interpret(p) -> str:
    if p.planned_total_cost == 0:
        return ("Sem orçamento planejado. Registre operações planejadas (PlannedEvent) "
                "para comparar planejado x realizado.")
    status = "ACIMA" if p.over_budget else "dentro"
    base = (f"Você gastou R$ {p.actual_total_cost:.2f} de R$ {p.planned_total_cost:.2f} "
            f"planejados ({p.pct_budget_spent}% do orçamento) — {status} do planejado. "
            f"Faltam R$ {p.remaining_budget:.2f}. Aplicações: {p.actual_applications} de "
            f"{p.planned_applications} planejadas.")
    if p.expected_profit is not None:
        base += f" Lucro esperado (a preço informado): R$ {p.expected_profit:.2f}."
    return base
