from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.historial import HistorialFilter, HistorialResponse
from ..services.historial_service import HistorialService

router = APIRouter()


@router.get("/", response_model=list[HistorialResponse])
def list_historial(
    parada_id: int | None = Query(None),
    tipo: str | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    catalogo_id: int | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    filters = HistorialFilter(
        parada_id=parada_id,
        tipo=tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        catalogo_id=catalogo_id,
    )
    service = HistorialService(db)
    return service.get_all(filters)
