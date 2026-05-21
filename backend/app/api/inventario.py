from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.inventario import InventarioResponse, UbicacionUpdate
from ..services.inventario_service import InventarioService

router = APIRouter()


@router.get("/", response_model=list[InventarioResponse])
def list_inventario(
    estado: str | None = Query(None),
    ubicacion: str | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_all(estado=estado, ubicacion=ubicacion)


@router.get("/buscar", response_model=list[InventarioResponse])
def buscar_por_short_code(
    short_code: str = Query(min_length=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_by_short_code(short_code)


@router.get("/{inventario_id}", response_model=InventarioResponse)
def get_inventario(
    inventario_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_by_id(inventario_id)


@router.put("/{inventario_id}/ubicacion", response_model=InventarioResponse)
def cambiar_ubicacion(
    inventario_id: int,
    data: UbicacionUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("CAMBIAR_UBICACION")),
):
    service = InventarioService(db)
    return service.change_ubicacion(inventario_id, data.ubicacion_macro)
