"""Export CSV das operações da fazenda (baixo esforço, alta utilidade)."""

from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.infra.db import get_session
from app.infra.repositories import EventRepository, FarmRepository

router = APIRouter()

_HEADER = ["talhao", "safra", "data", "operacao", "produto", "quantidade", "unidade", "custo"]


@router.get("/farms/{farm_id}/operations.csv")
def export_operations_csv(
    farm_id: int, session: Session = Depends(get_session)
) -> Response:
    farms = FarmRepository(session)
    if farms.get_farm(farm_id) is None:
        raise HTTPException(404, f"Farm {farm_id} inexistente")
    events = EventRepository(session)
    fields = {f.id: f.name for f in farms.list_fields(farm_id)}

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_HEADER)
    for cycle in farms.list_cycles_by_farm(farm_id):
        field_name = fields.get(cycle.field_id, f"Talhão {cycle.field_id}")
        for e in events.list_by_cycle(cycle.id):
            writer.writerow([
                field_name, cycle.season.label, e.event_date.isoformat(),
                e.event_type.value, e.product_name or "", e.quantity if e.quantity is not None else "",
                e.unit or "", e.cost if e.cost is not None else "",
            ])
    return Response(
        content=buf.getvalue(), media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="fada_operacoes_{farm_id}.csv"'},
    )
