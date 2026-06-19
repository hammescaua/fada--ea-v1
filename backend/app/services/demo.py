"""Fazenda de demonstração — popula dados realistas para o sistema nunca parecer vazio.

Histórico (safras passadas com produtividade real, clima real) + safra corrente com
plano e gastos parciais, de modo que dashboard, insights, decisões e adaptive acendam.
Dados sintéticos (produtividades fabricadas sobre clima real).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from app.domain.farm import AgriculturalEvent, CropCycle, EventType, Farm, Field, Season
from app.domain.planning import PlannedEvent
from app.domain.yield_estimation import RegionalYieldModel
from app.infra.repositories import EventRepository, FarmRepository, PlanningRepository
from app.services.regional_fitted import regional_fitted_sc_ha

HORIZONTINA = 4309605
CURRENT_SEASON = "2026/27"
HISTORY_YEARS = range(2020, 2025)  # anos de colheita com histórico


@dataclass
class DemoService:
    farms: FarmRepository
    events: EventRepository
    planning: PlanningRepository
    model: RegionalYieldModel

    def seed(self) -> dict:
        farm = self.farms.add_farm(Farm(name="Fazenda Demonstração", municipality_code=HORIZONTINA))
        specs = [("Talhão Norte", 100, 1.10, 75), ("Talhão Sul", 80, 0.92, 52),
                 ("Talhão Leste", 90, 1.0, 55)]
        n_cycles = 0
        for name, area, factor, target in specs:
            field = self.farms.add_field(Field(farm_id=farm.id, name=name, area_ha=area))
            # Histórico (com produtividade real)
            for i, year in enumerate(HISTORY_YEARS):
                fitted = regional_fitted_sc_ha(self.model, HORIZONTINA, year)
                if "Leste" in name:
                    actual = round(fitted * (1.15 if i % 2 else 0.85), 1)  # instável
                else:
                    actual = round(fitted * factor + (0.5 if i % 2 else -0.5), 1)
                self.farms.add_cycle(CropCycle(
                    field_id=field.id, crop="soja",
                    season=Season.parse(f"{year - 1}/{str(year)[2:]}"),
                    area_ha=area, actual_yield_sc_ha=actual,
                ))
                n_cycles += 1
            # Safra corrente: plano + gastos parciais
            cycle = self.farms.add_cycle(CropCycle(
                field_id=field.id, crop="soja", season=Season.parse(CURRENT_SEASON),
                area_ha=area, target_yield_sc_ha=target, expected_price_per_bag=125.0,
            ))
            n_cycles += 1
            self._plan_and_spend(cycle.id, name)
        return {
            "farm_id": farm.id, "farm_name": farm.name,
            "n_fields": len(specs), "n_cycles": n_cycles, "season": CURRENT_SEASON,
            "message": "Fazenda de demonstração criada. Explore o painel.",
        }

    def _plan_and_spend(self, cycle_id: int, field_name: str) -> None:
        plan = [("BASE_FERTILIZATION", "2026-11-01", 100000),
                ("HERBICIDE", "2026-11-20", 18000),
                ("FUNGICIDE", "2027-01-10", 25000)]
        for et, d, cost in plan:
            self.planning.add_planned(PlannedEvent(
                crop_cycle_id=cycle_id, event_type=EventType(et),
                planned_date=date.fromisoformat(d), expected_cost=cost))
        # Norte estoura o orçamento; os demais dentro
        base_actual = 150000 if "Norte" in field_name else 95000
        self.events.add_event(AgriculturalEvent(
            crop_cycle_id=cycle_id, event_type=EventType.BASE_FERTILIZATION,
            event_date=date(2026, 11, 1), cost=base_actual, product_name="MAP"))
        self.events.add_event(AgriculturalEvent(
            crop_cycle_id=cycle_id, event_type=EventType.HERBICIDE,
            event_date=date(2026, 11, 20), cost=18000, product_name="Glifosato"))
