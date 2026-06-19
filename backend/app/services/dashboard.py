"""Dashboard da fazenda — agregação determinística para a /home.

Responde "por onde começar?": atenção, agenda, orçamento e insights — compondo as
camadas existentes. Sem IA generativa.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.infra.repositories import FarmRepository
from app.services.decisions import DecisionsService, FarmNotFound
from app.services.insights import InsightsService
from app.services.planning import PlanningService


@dataclass
class DashboardService:
    farms: FarmRepository
    decisions: DecisionsService
    planning: PlanningService
    insights: InsightsService

    def farm_dashboard(self, farm_id: int) -> dict:
        dec = self.decisions.decisions(farm_id)  # valida a fazenda (FarmNotFound)
        levels = {"alta": 0, "média": 0, "saudável": 0}
        for f in dec["fields"]:
            levels[f["attention_level"]] += 1
        top_attention = next((f for f in dec["fields"]
                              if f["attention_level"] in ("alta", "média")), None)

        cycles = self.farms.list_cycles_by_farm(farm_id)
        budget = {"planned_total": 0.0, "actual_total": 0.0, "remaining": 0.0}
        overdue = upcoming = 0
        next_op: dict | None = None
        if cycles:
            target_year = max(c.season.harvest_year for c in cycles)
            for c in (c for c in cycles if c.season.harvest_year == target_year):
                pva = self.planning.plan_vs_actual(c.id)
                budget["planned_total"] += pva["planned_total_cost"]
                budget["actual_total"] += pva["actual_total_cost"]
                budget["remaining"] += pva["remaining_budget"]
                ag = self.planning.agenda(c.id)
                overdue += ag["summary"]["atrasada"]
                upcoming += ag["summary"]["próxima"]
                for item in ag["items"]:
                    if item["status"] == "próxima" and (
                        next_op is None or item["planned_date"] < next_op["planned_date"]):
                        next_op = item
        budget = {k: round(v, 2) for k, v in budget.items()}
        budget["pct_consumed"] = (
            round(100 * budget["actual_total"] / budget["planned_total"], 1)
            if budget["planned_total"] else None)

        insights = self.insights.insights(farm_id)["insights"][:3]
        return {
            "farm_id": farm_id,
            "season": dec["season"],
            "n_fields": dec["n_fields"],
            "attention": {"levels": levels, "top": top_attention},
            "budget": budget,
            "agenda": {"overdue": overdue, "upcoming": upcoming, "next_operation": next_op},
            "insights": insights,
        }


__all__ = ["DashboardService", "FarmNotFound"]
