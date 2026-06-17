"""Repositórios: mapeiam ORM <-> entidades de domínio. Domínio nunca vê SQLAlchemy."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.farm import CropCycle, Farm, Field, Season, YieldObservation
from app.infra.models import CropCycleORM, FarmORM, FieldORM, YieldObservationORM


def _farm(o: FarmORM) -> Farm:
    return Farm(id=o.id, name=o.name, municipality_code=o.municipality_code,
                created_at=o.created_at)


def _field(o: FieldORM) -> Field:
    return Field(id=o.id, farm_id=o.farm_id, name=o.name, area_ha=o.area_ha,
                 latitude=o.latitude, longitude=o.longitude, created_at=o.created_at)


def _cycle(o: CropCycleORM) -> CropCycle:
    return CropCycle(id=o.id, field_id=o.field_id, crop=o.crop,
                     season=Season(o.season_label, o.harvest_year),
                     planting_date=o.planting_date, created_at=o.created_at)


def _obs(o: YieldObservationORM) -> YieldObservation:
    return YieldObservation(
        id=o.id, crop_cycle_id=o.crop_cycle_id, actual_yield_sc_ha=o.actual_yield_sc_ha,
        area_ha=o.area_ha, actual_planting_date=o.actual_planting_date,
        actual_harvest_date=o.actual_harvest_date, cultivar=o.cultivar,
        notes=o.notes, created_at=o.created_at,
    )


class FarmRepository:
    def __init__(self, session: Session) -> None:
        self.s = session

    def _save(self, o):
        self.s.add(o)
        self.s.commit()
        self.s.refresh(o)
        return o

    def add_farm(self, farm: Farm) -> Farm:
        o = FarmORM(name=farm.name, municipality_code=farm.municipality_code)
        return _farm(self._save(o))

    def list_farms(self) -> list[Farm]:
        return [_farm(o) for o in self.s.scalars(select(FarmORM).order_by(FarmORM.id))]

    def get_farm(self, farm_id: int) -> Farm | None:
        o = self.s.get(FarmORM, farm_id)
        return _farm(o) if o else None

    def add_field(self, f: Field) -> Field:
        if self.s.get(FarmORM, f.farm_id) is None:
            raise LookupError(f"Farm {f.farm_id} inexistente")
        o = FieldORM(farm_id=f.farm_id, name=f.name, area_ha=f.area_ha,
                     latitude=f.latitude, longitude=f.longitude)
        return _field(self._save(o))

    def list_fields(self, farm_id: int) -> list[Field]:
        stmt = select(FieldORM).where(FieldORM.farm_id == farm_id).order_by(FieldORM.id)
        return [_field(o) for o in self.s.scalars(stmt)]

    def add_cycle(self, c: CropCycle) -> CropCycle:
        if self.s.get(FieldORM, c.field_id) is None:
            raise LookupError(f"Field {c.field_id} inexistente")
        o = CropCycleORM(field_id=c.field_id, crop=c.crop, season_label=c.season.label,
                         harvest_year=c.season.harvest_year, planting_date=c.planting_date)
        return _cycle(self._save(o))

    def add_observation(self, obs: YieldObservation) -> YieldObservation:
        if self.s.get(CropCycleORM, obs.crop_cycle_id) is None:
            raise LookupError(f"CropCycle {obs.crop_cycle_id} inexistente")
        o = YieldObservationORM(
            crop_cycle_id=obs.crop_cycle_id, actual_yield_sc_ha=obs.actual_yield_sc_ha,
            area_ha=obs.area_ha, actual_planting_date=obs.actual_planting_date,
            actual_harvest_date=obs.actual_harvest_date, cultivar=obs.cultivar, notes=obs.notes,
        )
        return _obs(self._save(o))

    def list_observations(self) -> list[YieldObservation]:
        stmt = select(YieldObservationORM).order_by(YieldObservationORM.id)
        return [_obs(o) for o in self.s.scalars(stmt)]
