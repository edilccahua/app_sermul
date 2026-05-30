from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.inventario import StockResponse, HerramientaEnUsoResponse, AjusteStockRequest
from ..services.inventario_service import InventarioService

router = APIRouter()


@router.get("/", response_model=list[StockResponse])
def list_stock(
    tipo_material: str | None = Query(None),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_all(tipo_material=tipo_material)


@router.get("/buscar", response_model=list[StockResponse])
def buscar_por_short_code(
    short_code: str = Query(min_length=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_by_short_code(short_code)


@router.get("/en-uso/grupo/{grupo_id}", response_model=list[HerramientaEnUsoResponse], dependencies=[Depends(RequirePermission("VER_INVENTARIO"))])
def herramientas_en_uso_por_grupo(
    grupo_id: int,
    db: Session = Depends(get_db),
):
    service = InventarioService(db)
    return service.get_en_uso_por_grupo(grupo_id)


@router.get("/{catalogo_id}", response_model=StockResponse)
def get_stock(
    catalogo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = InventarioService(db)
    return service.get_by_id(catalogo_id)


@router.post("/ajuste", response_model=StockResponse)
def ajustar_stock(
    data: AjusteStockRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(RequirePermission("EDITAR_INVENTARIO")),
):
    service = InventarioService(db)
    return service.ajustar_stock(current_user.id, data)
