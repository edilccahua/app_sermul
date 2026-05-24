from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..api.deps import RequirePermission
from ..core.database import get_db
from ..models.usuario import Usuario
from ..schemas.catalogo import CatalogoCreate, CatalogoResponse, CatalogoUpdate
from ..services.catalogo_service import CatalogoService

router = APIRouter()


@router.get("/", response_model=list[CatalogoResponse])
def list_catalogo(
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = CatalogoService(db)
    return service.get_all()


@router.get("/search", response_model=list[CatalogoResponse])
def search_catalogo(
    q: str = Query(min_length=1),
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = CatalogoService(db)
    return service.search(q)


@router.get("/{catalogo_id}", response_model=CatalogoResponse)
def get_catalogo(
    catalogo_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("VER_INVENTARIO")),
):
    service = CatalogoService(db)
    return service.get_by_id(catalogo_id)


@router.post("/", response_model=CatalogoResponse, status_code=201)
def create_catalogo(
    data: CatalogoCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("EDITAR_INVENTARIO")),
):
    service = CatalogoService(db)
    return service.create(data)


@router.put("/{catalogo_id}", response_model=CatalogoResponse)
def update_catalogo(
    catalogo_id: int,
    data: CatalogoUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("EDITAR_INVENTARIO")),
):
    service = CatalogoService(db)
    return service.update(catalogo_id, data)


@router.put("/{catalogo_id}/stock", response_model=CatalogoResponse)
def update_stock(
    catalogo_id: int,
    field: str,
    delta: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(RequirePermission("EDITAR_INVENTARIO")),
):
    service = CatalogoService(db)
    try:
        return service.update_stock(catalogo_id, field, delta)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
