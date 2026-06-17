"""Modelos ORM (tabelas). Separados das entidades de domínio (mapeadas nos repos)."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infra.db import Base


class FarmORM(Base):
    __tablename__ = "farms"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    municipality_code: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    fields: Mapped[list[FieldORM]] = relationship(
        back_populates="farm", cascade="all, delete-orphan"
    )


class FieldORM(Base):
    __tablename__ = "fields"

    id: Mapped[int] = mapped_column(primary_key=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id"))
    name: Mapped[str] = mapped_column(String(200))
    area_ha: Mapped[float] = mapped_column(Float)
    latitude: Mapped[float | None]
    longitude: Mapped[float | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    farm: Mapped[FarmORM] = relationship(back_populates="fields")
    cycles: Mapped[list[CropCycleORM]] = relationship(
        back_populates="field", cascade="all, delete-orphan"
    )


class CropCycleORM(Base):
    __tablename__ = "crop_cycles"

    id: Mapped[int] = mapped_column(primary_key=True)
    field_id: Mapped[int] = mapped_column(ForeignKey("fields.id"))
    crop: Mapped[str] = mapped_column(String(60))
    season_label: Mapped[str] = mapped_column(String(20))
    harvest_year: Mapped[int]
    planting_date: Mapped[date | None]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    field: Mapped[FieldORM] = relationship(back_populates="cycles")
    observations: Mapped[list[YieldObservationORM]] = relationship(
        back_populates="cycle", cascade="all, delete-orphan"
    )


class YieldObservationORM(Base):
    __tablename__ = "yield_observations"

    id: Mapped[int] = mapped_column(primary_key=True)
    crop_cycle_id: Mapped[int] = mapped_column(ForeignKey("crop_cycles.id"))
    actual_yield_sc_ha: Mapped[float] = mapped_column(Float)
    area_ha: Mapped[float] = mapped_column(Float)
    actual_planting_date: Mapped[date | None]
    actual_harvest_date: Mapped[date | None]
    cultivar: Mapped[str | None] = mapped_column(String(120), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    cycle: Mapped[CropCycleORM] = relationship(back_populates="observations")
