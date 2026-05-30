from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.historial import HistorialFilter, HistorialPaginadoResponse, HistorialResponse
from ..services.historial_service import HistorialService

router = APIRouter()


@router.get("/", response_model=HistorialPaginadoResponse)
def list_historial(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    parada_id: int | None = Query(None),
    tipo: str | None = Query(None),
    fecha_desde: datetime | None = Query(None),
    fecha_hasta: datetime | None = Query(None),
    catalogo_id: int | None = Query(None),
    grupo_destino_id: int | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    filters = HistorialFilter(
        parada_id=parada_id,
        tipo=tipo,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        catalogo_id=catalogo_id,
        grupo_destino_id=grupo_destino_id,
        search=search,
    )
    service = HistorialService(db)
    resultados, total = service.get_all(filters, offset=offset, limit=limit)
    return HistorialPaginadoResponse(
        items=resultados,  # type: ignore[arg-type]
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/{historial_id}", response_model=HistorialResponse)
def get_historial_by_id(
    historial_id: str,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = HistorialService(db)
    resultado = service.get_by_id(historial_id)
    if not resultado:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Movimiento no encontrado")
    return resultado
